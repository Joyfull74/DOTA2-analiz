import os
import sys
import requests
import datetime
import json

# ============= НАСТРОЙКИ =============
MWS_TOKEN = os.environ.get('MWS_TOKEN')
TABLE_ID = "dstWj25HjQqwT4jmdC"
VIEW_ID = "viw3UUhw6Xy2w"
# ======================================

API_URL = "https://tables.mws.ru/api/v1"

# Принудительный сброс буфера вывода
print = lambda *args, **kwargs: __import__('builtins').print(*args, **kwargs, flush=True)

def get_pro_matches():
    """Получает последние профессиональные матчи"""
    url = "https://api.opendota.com/api/proMatches"
    try:
        print(f"📡 Запрос к OpenDota API...")
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        print(f"✅ Получено {len(data)} матчей")
        return data
    except Exception as e:
        print(f"❌ Ошибка OpenDota: {e}")
        return []

def create_record_payload(match):
    """Создаёт запись в формате MWS Tables (поля напрямую)"""
    
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
    
    # Отправляем поля напрямую, без обёртки "fields"
    record = {
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
    
    return record

def send_to_mws(record, match_id):
    """Отправляет запись в MWS Tables"""
    
    headers = {
        'Authorization': f'Bearer {MWS_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    url = f"{API_URL}/datasets/{TABLE_ID}/records"
    params = {'viewId': VIEW_ID}
    
    print(f"\n📤 Отправка матча {match_id}...")
    print(f"URL: {url}")
    print(f"Данные: {json.dumps(record, ensure_ascii=False, indent=2)}")
    
    try:
        # Отправляем запись как есть (без fields)
        response = requests.post(url, headers=headers, params=params, json=record)
        print(f"📥 Статус ответа: {response.status_code}")
        print(f"📥 Тело ответа: {response.text}")
        
        if response.status_code in [200, 201]:
            print(f"✅ Успешно!")
            return True
        else:
            print(f"❌ Ошибка!")
            return False
            
    except Exception as e:
        print(f"❌ Исключение: {e}")
        return False

def main():
    print("=" * 50)
    print("🚀 ЗАПУСК ПАРСЕРА DOTA 2")
    print(f"🕐 Время: {datetime.datetime.now()}")
    print("=" * 50)
    
    # Проверка токена
    if not MWS_TOKEN:
        print("❌ ОШИБКА: MWS_TOKEN не задан!")
        return
    print("✅ MWS_TOKEN найден")
    
    # Проверка ID
    print(f"📋 TABLE_ID: {TABLE_ID}")
    print(f"📋 VIEW_ID: {VIEW_ID}")
    
    # Получаем матчи
    matches = get_pro_matches()
    if not matches:
        print("❌ Нет матчей для обработки")
        return
    
    # Обрабатываем первые 3 матча
    successful = 0
    for i, match in enumerate(matches[:3]):
        match_id = match.get('match_id')
        print(f"\n{'='*30}")
        print(f"⚙️ Матч {i+1}/3 (ID: {match_id})")
        
        # Показываем сырые данные из OpenDota
        print(f"📊 Сырые данные матча:")
        print(f"   radiant_name: {match.get('radiant_name')}")
        print(f"   dire_name: {match.get('dire_name')}")
        print(f"   radiant_win: {match.get('radiant_win')}")
        print(f"   duration: {match.get('duration')}")
        print(f"   radiant_score: {match.get('radiant_score')}")
        print(f"   dire_score: {match.get('dire_score')}")
        print(f"   league_name: {match.get('league_name')}")
        print(f"   start_time: {match.get('start_time')}")
        
        record = create_record_payload(match)
        if send_to_mws(record, match_id):
            successful += 1
    
    print(f"\n{'='*50}")
    print(f"✅ ГОТОВО! Успешно добавлено: {successful}/3")
    print(f"{'='*50}")

if __name__ == "__main__":
    main()
