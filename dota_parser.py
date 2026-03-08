import os
import requests
import datetime

# ============= НАСТРОЙКИ =============
MWS_TOKEN = os.environ.get('MWS_TOKEN')
MWS_TABLE_ID = "dstWj25HjQqwT4jmDC"  # ID из документации
VIEW_ID = "viw3UUhw6Xy2w"            # ID представления
# ======================================

# API endpoint из документации
MWS_API_URL = "https://tables.mws.ru/fusion/v1"

# Field ID для поля (из документации)
FIELD_ID = "fldkN4EjwFeEP"

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

def process_match(match, index):
    """Превращает матч в формат для MWS Tables"""
    
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
    
    # Формируем строку со ВСЕМИ значениями, разделенными специальным разделителем
    # MWS Tables ожидает все поля в одном field ID
    values = [
        str(match.get('match_id', '')),
        match.get('radiant_name') or 'Unknown',
        match.get('dire_name') or 'Unknown',
        'Radiant' if match.get('radiant_win') else 'Dire',
        f"{duration_min}:{duration_sec:02d}",
        f"{match.get('radiant_score', 0)} - {match.get('dire_score', 0)}",
        match.get('league_name') or 'No League',
        'Yes' if had_megacreeps else 'No',
        match_date
    ]
    
    # Объединяем все значения через разделитель (например, " | ")
    # Так MWS Tables поймет, где какое поле
    combined_value = " | ".join(values)
    
    return {
        "fields": {
            FIELD_ID: combined_value
        }
    }

def append_to_mws_tables(matches):
    """Добавляет матчи в MWS Tables"""
    if not MWS_TOKEN:
        print("⚠️ MWS_TOKEN не настроен")
        return
    
    headers = {
        'Authorization': f'Bearer {MWS_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    # Формируем URL как в документации
    url = f"{MWS_API_URL}/datasets/{MWS_TABLE_ID}/records"
    params = {
        'viewId': VIEW_ID,
        'fieldKey': 'id'
    }
    
    # Создаём records в правильном формате
    records = []
    for i, match in enumerate(matches):
        record = {
            "fields": {
                FIELD_ID: match["fields"][FIELD_ID]
            }
        }
        records.append(record)
        print(f"📝 Подготовлен матч {i+1}: {match['fields'][FIELD_ID][:50]}...")
    
    # Финальный payload точно как в документации
    payload = {
        "records": records,
        "fieldKey": "id"
    }
    
    print(f"\n📤 Отправляем {len(records)} записей...")
    
    try:
        response = requests.post(url, headers=headers, params=params, json=payload)
        
        if response.status_code in [200, 201]:
            print(f"✅ УСПЕХ! Все {len(records)} записей добавлены")
            print(f"Ответ: {response.text[:200]}")
        else:
            print(f"❌ Ошибка {response.status_code}")
            print(f"Ответ: {response.text[:500]}")
            
    except Exception as e:
        print(f"❌ Исключение: {e}")

def main():
    print(f"🚀 Запуск парсера Dota 2: {datetime.datetime.now()}")
    
    matches = get_pro_matches()
    if not matches:
        print("❌ Нет матчей")
        return
    
    print(f"📊 Получено {len(matches)} матчей")
    
    # Берём первые 5 матчей для теста
    test_matches = []
    for i, match in enumerate(matches[:5]):
        processed = process_match(match, i)
        test_matches.append(processed)
        print(f"⚙️ Обработан матч {match.get('match_id')}")
    
    # Отправляем в MWS Tables
    append_to_mws_tables(test_matches)
    print("✅ Готово!")

if __name__ == "__main__":
    main()
