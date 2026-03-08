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

# Создаём файл для лога
log_file = open('debug_log.txt', 'w', encoding='utf-8')

def log_print(*args, **kwargs):
    """Печатает и в консоль, и в файл"""
    print(*args, **kwargs, flush=True)
    print(*args, **kwargs, file=log_file, flush=True)

def get_pro_matches():
    """Получает последние профессиональные матчи"""
    url = "https://api.opendota.com/api/proMatches"
    try:
        log_print(f"📡 Запрос к OpenDota API...")
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        log_print(f"✅ Получено {len(data)} матчей")
        return data
    except Exception as e:
        log_print(f"❌ Ошибка OpenDota: {e}")
        return []

def create_record_payload(match):
    """Создаёт запись в формате MWS Tables"""
    
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
    
    record = {
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
    
    return record

def send_to_mws(record, match_id):
    """Отправляет запись в MWS Tables"""
    
    headers = {
        'Authorization': f'Bearer {MWS_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    url = f"{API_URL}/datasets/{TABLE_ID}/records"
    params = {'viewId': VIEW_ID}
    
    log_print(f"\n📤 Отправка матча {match_id}...")
    log_print(f"URL: {url}")
    log_print(f"Данные: {json.dumps(record, ensure_ascii=False, indent=2)}")
    
    try:
        response = requests.post(url, headers=headers, params=params, json=record)
        log_print(f"📥 Статус ответа: {response.status_code}")
        log_print(f"📥 Заголовки ответа: {dict(response.headers)}")
        log_print(f"📥 Тело ответа: {response.text}")
        
        if response.status_code in [200, 201]:
            log_print(f"✅ Успешно!")
            return True
        else:
            log_print(f"❌ Ошибка!")
            return False
            
    except Exception as e:
        log_print(f"❌ Исключение: {e}")
        return False

def main():
    log_print("=" * 50)
    log_print("🚀 ЗАПУСК ПАРСЕРА DOTA 2")
    log_print(f"🕐 Время: {datetime.datetime.now()}")
    log_print("=" * 50)
    
    # Проверка токена
    if not MWS_TOKEN:
        log_print("❌ ОШИБКА: MWS_TOKEN не задан!")
        log_file.close()
        return
    log_print("✅ MWS_TOKEN найден")
    
    # Проверка ID
    log_print(f"📋 TABLE_ID: {TABLE_ID}")
    log_print(f"📋 VIEW_ID: {VIEW_ID}")
    
    # Получаем матчи
    matches = get_pro_matches()
    if not matches:
        log_print("❌ Нет матчей для обработки")
        log_file.close()
        return
    
    # Обрабатываем первые 3 матча
    successful = 0
    for i, match in enumerate(matches[:3]):
        match_id = match.get('match_id')
        log_print(f"\n{'='*30}")
        log_print(f"⚙️ Матч {i+1}/3 (ID: {match_id})")
        
        # Показываем сырые данные из OpenDota
        log_print(f"📊 Сырые данные матча:")
        log_print(f"   radiant_name: {match.get('radiant_name')}")
        log_print(f"   dire_name: {match.get('dire_name')}")
        log_print(f"   radiant_win: {match.get('radiant_win')}")
        log_print(f"   duration: {match.get('duration')}")
        log_print(f"   radiant_score: {match.get('radiant_score')}")
        log_print(f"   dire_score: {match.get('dire_score')}")
        log_print(f"   league_name: {match.get('league_name')}")
        log_print(f"   start_time: {match.get('start_time')}")
        
        record = create_record_payload(match)
        if send_to_mws(record, match_id):
            successful += 1
    
    log_print(f"\n{'='*50}")
    log_print(f"✅ ГОТОВО! Успешно добавлено: {successful}/3")
    log_print(f"{'='*50}")
    
    # Закрываем файл лога
    log_file.close()
    
    # Пытаемся прочитать и вывести содержимое файла
    try:
        with open('debug_log.txt', 'r', encoding='utf-8') as f:
            print("\n" + "="*50)
            print("📁 СОДЕРЖИМОЕ ФАЙЛА debug_log.txt:")
            print("="*50)
            print(f.read())
    except:
        pass

if __name__ == "__main__":
    main()
