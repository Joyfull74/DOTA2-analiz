import os
import requests
import datetime

# ============= НАСТРОЙКИ =============
MWS_TOKEN = os.environ.get('MWS_TOKEN')
MWS_TABLE_ID = os.environ.get('MWS_TABLE_ID')
# ======================================

# API endpoint
MWS_API_URL = "https://tables.mws.ru/api"

def get_pro_matches():
    """Получает последние профессиональные матчи"""
    url = "https://api.opendota.com/api/proMatches"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ Ошибка OpenDota: {e}")
        return []

def process_match(match):
    """Превращает матч в список значений в правильном порядке"""
    
    # Проверка мегакрипов
    had_megacreeps = (match.get('barracks_status_radiant') == 0 or 
                     match.get('barracks_status_dire') == 0)
    
    # Длительность
    duration_seconds = match.get('duration', 0)
    duration_min = duration_seconds // 60
    duration_sec = duration_seconds % 60
    
    # Дата
    start_time = match.get('start_time')
    if start_time:
        match_date = datetime.datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M')
    else:
        match_date = ''
    
    # ВОЗВРАЩАЕМ СПИСОК ЗНАЧЕНИЙ В ТОМ ПОРЯДКЕ, 
    # В КОТОРОМ СОЗДАНЫ КОЛОНКИ В ТАБЛИЦЕ:
    return [
        str(match.get('match_id', '')),                    # 1. match_id
        match.get('radiant_name') or 'Unknown',            # 2. radiant_team
        match.get('dire_name') or 'Unknown',               # 3. dire_team
        'Radiant' if match.get('radiant_win') else 'Dire', # 4. winner
        f"{duration_min}:{duration_sec:02d}",              # 5. duration
        f"{match.get('radiant_score', 0)} - {match.get('dire_score', 0)}", # 6. score
        match.get('league_name') or 'No League',           # 7. league
        'Yes' if had_megacreeps else 'No',                 # 8. had_megacreeps
        match_date                                          # 9. match_date
    ]

def append_to_mws_tables(matches):
    """Добавляет матчи в MWS Tables"""
    if not all([MWS_TOKEN, MWS_TABLE_ID]):
        print("⚠️ MWS Tables не настроены")
        return
    
    headers = {
        'Authorization': f'Bearer {MWS_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    # Правильный endpoint (взят из твоего скриншота с панелью API)
    endpoint = f"{MWS_API_URL}/tables/{MWS_TABLE_ID}/rows"
    
    for match_list in matches:
        # Отправляем как простой массив значений
        payload = match_list
        
        try:
            response = requests.post(endpoint, headers=headers, json=payload)
            
            if response.status_code in [200, 201]:
                print(f"✅ Матч {match_list[0]} успешно добавлен!")
            else:
                print(f"❌ Ошибка {response.status_code} для матча {match_list[0]}")
                print(f"Ответ: {response.text[:200]}")
                
        except Exception as e:
            print(f"❌ Исключение для матча {match_list[0]}: {e}")

def main():
    print(f"🚀 Запуск парсера Dota 2: {datetime.datetime.now()}")
    
    matches = get_pro_matches()
    if not matches:
        print("❌ Нет матчей")
        return
    
    print(f"📊 Получено {len(matches)} матчей")
    
    # Берём первые 10 матчей для теста
    test_matches = []
    for match in matches[:10]:
        processed = process_match(match)
        test_matches.append(processed)
        print(f"⚙️ Подготовлен матч {processed[0]}")
    
    # Отправляем в MWS Tables
    append_to_mws_tables(test_matches)
    print("✅ Готово!")

if __name__ == "__main__":
    main()
