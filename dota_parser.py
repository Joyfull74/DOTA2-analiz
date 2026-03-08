import os
import sys
import requests
import datetime
import json

# ============= НАСТРОЙКИ =============
MWS_TOKEN = os.environ.get('MWS_TOKEN')
VIEW_ID = "viw3UUhw6Xy2w"
# ======================================

API_URL = "https://tables.mws.ru/api/v1"

# Все возможные ID таблицы
TABLE_IDS = [
    "dstWj25HjQqwT4jmdC",  # из основного URL
    "viw3UUhw6Xy2w",       # ID представления
    "shrdTUtqSMEl2S5URWuR7", # из ссылки поделиться
    "recul0FclA6MW",       # ID конкретной записи
    "fldkN4EjwFeEP",       # Field ID
]

print = lambda *args, **kwargs: __import__('builtins').print(*args, **kwargs, flush=True)

def get_pro_matches():
    url = "https://api.opendota.com/api/proMatches"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ Ошибка OpenDota: {e}")
        return []

def create_record_payload(match):
    had_megacreeps = (match.get('barracks_status_radiant') == 0 or 
                     match.get('barracks_status_dire') == 0)
    
    duration_seconds = match.get('duration', 0)
    duration_min = duration_seconds // 60
    duration_sec = duration_seconds % 60
    
    start_time = match.get('start_time')
    if start_time:
        match_date = datetime.datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M')
    else:
        match_date = ''
    
    return {
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

def send_to_mws(record, match_id, table_id):
    headers = {
        'Authorization': f'Bearer {MWS_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    url = f"{API_URL}/datasets/{table_id}/records"
    params = {'viewId': VIEW_ID}
    
    print(f"\n📤 Отправка матча {match_id} в таблицу {table_id}...")
    
    try:
        response = requests.post(url, headers=headers, params=params, json=record)
        print(f"📥 Статус ответа: {response.status_code}")
        print(f"📥 Тело ответа: {response.text}")
        
        if response.status_code in [200, 201]:
            return True
        return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def main():
    print("=" * 50)
    print("🚀 ПОИСК РАБОЧЕГО ID ТАБЛИЦЫ")
    print("=" * 50)
    
    matches = get_pro_matches()
    if not matches:
        return
    
    match = matches[0]
    record = create_record_payload(match)
    
    for table_id in TABLE_IDS:
        print(f"\n{'='*30}")
        print(f"🔍 Пробуем ID: {table_id}")
        success = send_to_mws(record, match.get('match_id'), table_id)
        if success:
            print(f"✅ НАЙДЕН РАБОЧИЙ ID: {table_id}")
            break
    
    print("\n✅ Поиск завершён")

if __name__ == "__main__":
    main()
