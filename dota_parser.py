import os
import requests
import datetime

# ============= НАСТРОЙКИ =============
MWS_TOKEN = os.environ.get('MWS_TOKEN')
TABLE_ID = "dstWj25HjQqwT4jmdC"      # ID таблицы
VIEW_ID = "viw3UUhw6Xy2w"             # ID представления
# ======================================

API_URL = "https://tables.mws.ru/fusion/v1"

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

def create_record(match):
    """Создаёт запись в формате MWS Tables"""
    
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
    
    # Формируем запись с полями (как в примерах на GitHub)
    return {
        "fields": {
            "match_id": str(match.get('match_id', '')),
            "radiant_team": match.get('radiant_name') or 'Unknown',
            "dire_team": match.get('dire_name') or 'Unknown',
            "winner": 'Radiant' if match.get('radiant_win') else 'Dire',
            "duration": f"{duration_min}:{duration_sec:02d}",
            "score": f"{match.get('radiant_score', 0)} - {match.get('dire_score', 0)}",
            "league": match.get('league_name') or 'No League',
            "had_megacreeps": 'Yes' if had_megacreeps else 'No',
            "match_date": match_date
        }
    }

def send_to_mws(record):
    """Отправляет запись в MWS Tables"""
    
    headers = {
        'Authorization': f'Bearer {MWS_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    # Эндпоинт для создания записи
    url = f"{API_URL}/datasets/{TABLE_ID}/records"
    params = {'viewId': VIEW_ID}
    
    try:
        response = requests.post(url, headers=headers, params=params, json=record)
        
        if response.status_code in [200, 201]:
            print(f"✅ Запись успешно добавлена!")
            return True
        else:
            print(f"❌ Ошибка {response.status_code}")
            print(f"Ответ: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Исключение: {e}")
        return False

def main():
    print(f"🚀 Запуск: {datetime.datetime.now()}")
    
    matches = get_pro_matches()
    if not matches:
        return
    
    print(f"📊 Получено {len(matches)} матчей")
    
    # Берём 1 матч для теста
    match = matches[0]
    print(f"⚙️ Обрабатываю матч {match.get('match_id')}")
    
    record = create_record(match)
    print(f"📝 Запись подготовлена")
    
    success = send_to_mws(record)
    
    if success:
        print("✅ Готово! Проверь таблицу")
    else:
        print("❌ Что-то пошло не так")

if __name__ == "__main__":
    main()
