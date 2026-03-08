import os
import requests
import datetime

# ============= НАСТРОЙКИ =============
MWS_TOKEN = os.environ.get('MWS_TOKEN')
MWS_TABLE_ID = os.environ.get('MWS_TABLE_ID')
# ======================================

# API endpoint для MWS Tables (уточни в документации!)
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
        'match_id': str(match.get('match_id', '')),
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
    
    # Пробуем разные возможные endpoint'ы
    possible_urls = [
        f"{MWS_API_URL}/tables/{MWS_TABLE_ID}/rows",
        f"{MWS_API_URL}/bases/{MWS_TABLE_ID}/rows",
        f"{MWS_API_URL}/tables/{MWS_TABLE_ID}/records"
    ]
    
    for url in possible_urls:
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                existing_ids = []
                
                # Пробуем разные форматы ответа
                if isinstance(data, list):
                    for row in data:
                        if isinstance(row, dict) and 'match_id' in row:
                            existing_ids.append(str(row['match_id']))
                elif isinstance(data, dict) and 'rows' in data:
                    for row in data['rows']:
                        if 'match_id' in row:
                            existing_ids.append(str(row['match_id']))
                elif isinstance(data, dict) and 'data' in data:
                    for row in data['data']:
                        if 'match_id' in row:
                            existing_ids.append(str(row['match_id']))
                
                print(f"📋 Найдено {len(existing_ids)} существующих матчей")
                return existing_ids
        except:
            continue
    
    print("⚠️ Не удалось получить существующие матчи, продолжаем без проверки дубликатов")
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
    
    # Пробуем разные форматы отправки данных
    urls_and_formats = [
        {
            'url': f"{MWS_API_URL}/tables/{MWS_TABLE_ID}/rows",
            'format': 'list'
        },
        {
            'url': f"{MWS_API_URL}/bases/{MWS_TABLE_ID}/rows",
            'format': 'list'
        },
        {
            'url': f"{MWS_API_URL}/tables/{MWS_TABLE_ID}/records",
            'format': 'records'
        },
        {
            'url': f"{MWS_API_URL}/tables/{MWS_TABLE_ID}/rows/batch",
            'format': 'batch'
        }
    ]
    
    for match in new_matches:
        for attempt in urls_and_formats:
            try:
                if attempt['format'] == 'list':
                    # Простой список значений в правильном порядке
                    payload = [
                        match['match_id'],
                        match['radiant_team'],
                        match['dire_team'],
                        match['winner'],
                        match['duration'],
                        match['score'],
                        match['league'],
                        match['had_megacreeps'],
                        match['match_date']
                    ]
                elif attempt['format'] == 'records':
                    payload = {'records': [match]}
                elif attempt['format'] == 'batch':
                    payload = [match]
                else:
                    payload = match
                
                response = requests.post(attempt['url'], headers=headers, json=payload)
                
                if response.status_code in [200, 201]:
                    print(f"✅ Матч {match['match_id']} добавлен (формат: {attempt['format']})")
                    break
                else:
                    print(f"⏳ Пробуем другой формат для матча {match['match_id']}...")
            except Exception as e:
                continue
        else:
            print(f"❌ Не удалось добавить матч {match['match_id']} ни в одном формате")

def main():
    print(f"🚀 Запуск парсера Dota 2: {datetime.datetime.now()}")
    
    matches = get_pro_matches()
    if not matches:
        print("❌ Не удалось получить матчи")
        return
    
    print(f"📊 Получено {len(matches)} матчей")
    
    processed_matches = []
    for match in matches[:20]:
        processed = process_match(match)
        processed_matches.append(processed)
        print(f"⚙️ Обработан матч {processed['match_id']}")
    
    append_to_mws_tables(processed_matches)
    print("✅ Готово!")

if __name__ == "__main__":
    main()
