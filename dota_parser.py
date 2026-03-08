import os
import requests
import datetime

# ============= НАСТРОЙКИ =============
MWS_TOKEN = os.environ.get('MWS_TOKEN')        # API токен из MWS Tables
MWS_TABLE_ID = os.environ.get('MWS_TABLE_ID')  # ID вашей таблицы
# ======================================

MWS_API_URL = "https://tables.mws.ru/api/v1"

def get_pro_matches():
    """Получает последние профессиональные матчи через OpenDota API"""
    url = "https://api.opendota.com/api/proMatches"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка при запросе к OpenDota API: {e}")
        return []

def process_match(match):
    """Обрабатывает один матч"""
    # Проверяем мегакрипы (все казармы уничтожены)
    had_megacreeps = (match.get('barracks_status_radiant') == 0 or 
                     match.get('barracks_status_dire') == 0)
    
    # Длительность
    duration_seconds = match.get('duration', 0)
    duration_min = duration_seconds // 60
    duration_sec = duration_seconds % 60
    
    # Дата
    start_time = match.get('start_time')
    if start_time:
        match_date = datetime.datetime.fromtimestamp(start_time).isoformat()
    else:
        match_date = None
    
    return {
        'match_id': match.get('match_id'),
        'radiant_team': match.get('radiant_name') or 'Unknown',
        'dire_team': match.get('dire_name') or 'Unknown',
        'winner': 'Radiant' if match.get('radiant_win') else 'Dire',
        'duration': f"{duration_min}:{duration_sec:02d}",
        'score': f"{match.get('radiant_score', 0)} - {match.get('dire_score', 0)}",
        'league': match.get('league_name') or 'No League',
        'had_megacreeps': 'Yes' if had_megacreeps else 'No',
        'match_date': match_date,
    }

def get_existing_match_ids():
    """Получает существующие match_id из MWS Tables"""
    if not all([MWS_TOKEN, MWS_TABLE_ID]):
        return []
    
    headers = {'Authorization': f'Bearer {MWS_TOKEN}'}
    url = f"{MWS_API_URL}/tables/{MWS_TABLE_ID}/rows"
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        existing_ids = []
        if isinstance(data, list):
            for row in data:
                if 'match_id' in row:
                    existing_ids.append(str(row['match_id']))
        return existing_ids
    except Exception as e:
        print(f"❌ Ошибка при получении существующих матчей: {e}")
        return []

def append_to_mws_tables(matches):
    """Добавляет новые матчи в MWS Tables"""
    if not all([MWS_TOKEN, MWS_TABLE_ID]):
        print("⚠️ MWS Tables не настроены, пропускаю сохранение")
        return
    
    existing_ids = get_existing_match_ids()
    new_matches = [m for m in matches if str(m['match_id']) not in existing_ids]
    
    if not new_matches:
        print("📭 Новых матчей нет")
        return
    
    headers = {
        'Authorization': f'Bearer {MWS_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    for match in new_matches:
        url = f"{MWS_API_URL}/tables/{MWS_TABLE_ID}/rows"
        try:
            response = requests.post(url, headers=headers, json=match)
            response.raise_for_status()
            print(f"✅ Матч {match['match_id']} добавлен")
        except Exception as e:
            print(f"❌ Ошибка при добавлении матча {match['match_id']}: {e}")

def main():
    print(f"🚀 Запуск парсера Dota 2: {datetime.datetime.now()}")
    
    matches = get_pro_matches()
    if not matches:
        print("❌ Не удалось получить матчи")
        return
    
    print(f"📊 Получено {len(matches)} матчей")
    
    processed_matches = []
    for match in matches[:20]:  # первые 20 матчей
        processed = process_match(match)
        processed_matches.append(processed)
        print(f"⚙️ Обработан матч {processed['match_id']}")
    
    append_to_mws_tables(processed_matches)
    print("✅ Готово!")

if __name__ == "__main__":
    main()
