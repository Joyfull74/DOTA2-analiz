import os
import sys
import requests
import datetime
import json

MWS_TOKEN = os.environ.get('MWS_TOKEN')
TABLE_ID = "dstWj25HjQqwT4jmdC"
VIEW_ID = "viw3UUhw6Xy2w"
API_URL = "https://tables.mws.ru/api/v1"

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

def send_to_mws(record, match_id):
    headers = {
        'Authorization': f'Bearer {MWS_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    # Пробуем разные варианты
    variants = [
        {
            'name': 'datasets + один объект',
            'url': f"{API_URL}/datasets/{TABLE_ID}/records",
            'data': record
        },
        {
            'name': 'tables + один объект',
            'url': f"{API_URL}/tables/{TABLE_ID}/records",
            'data': record
        },
        {
            'name': 'datasets + массив',
            'url': f"{API_URL}/datasets/{TABLE_ID}/records",
            'data': [record]
        },
        {
            'name': 'tables + массив',
            'url': f"{API_URL}/tables/{TABLE_ID}/records",
            'data': [record]
        }
    ]
    
    params = {'viewId': VIEW_ID}
    
    for variant in variants:
        print(f"\n📤 Пробуем: {variant['name']}")
        print(f"URL: {variant['url']}")
        
        try:
            response = requests.post(variant['url'], headers=headers, params=params, json=variant['data'])
            print(f"📥 Статус: {response.status_code}")
            print(f"📥 Ответ: {response.text}")
            
            if response.status_code in [200, 201]:
                # Проверяем, действительно ли данные добавились
                if 'success' in response.text and 'true' in response.text.lower():
                    print(f"✅ УСПЕХ с вариантом: {variant['name']}")
                    return True
        except Exception as e:
            print(f"❌ Ошибка: {e}")
    
    return False

def main():
    print("=" * 50)
    print("🚀 ФИНАЛЬНОЕ ТЕСТИРОВАНИЕ")
    print("=" * 50)
    
    matches = get_pro_matches()
    if not matches:
        return
    
    match = matches[0]
    record = create_record_payload(match)
    print(f"\n⚙️ Тестовый матч: {match.get('match_id')}")
    
    success = send_to_mws(record, match.get('match_id'))
    
    if success:
        print("\n✅ РАБОТАЕТ! Проверь таблицу!")
    else:
        print("\n❌ Ни один вариант не сработал")

if __name__ == "__main__":
    main()
