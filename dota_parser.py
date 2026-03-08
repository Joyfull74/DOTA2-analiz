import os
import requests
import datetime
import json

# ============= НАСТРОЙКИ =============
MWS_TOKEN = os.environ.get('MWS_TOKEN')
MWS_TABLE_ID = os.environ.get('MWS_TABLE_ID')
# ======================================

MWS_API_URL = "https://tables.mws.ru/api/v1"

def debug_print(title, data):
    """Печатает отладочную информацию"""
    print(f"\n🔍 {title}:")
    print(json.dumps(data, indent=2, ensure_ascii=False)[:500])

def test_mws_api():
    """Тестирует API и выводит информацию"""
    print("\n🧪 ТЕСТИРОВАНИЕ API MWS TABLES")
    
    headers = {'Authorization': f'Bearer {MWS_TOKEN}'}
    
    # Тест 1: Получить информацию о таблице
    print("\n1️⃣ Пробуем получить информацию о таблице...")
    urls = [
        f"{MWS_API_URL}/tables/{MWS_TABLE_ID}",
        f"{MWS_API_URL}/bases/{MWS_TABLE_ID}",
        f"{MWS_API_URL}/tables/{MWS_TABLE_ID}/info",
        f"{MWS_API_URL}/bases/{MWS_TABLE_ID}/info"
    ]
    
    for url in urls:
        try:
            response = requests.get(url, headers=headers)
            print(f"   URL: {url}")
            print(f"   Статус: {response.status_code}")
            if response.status_code == 200:
                debug_print("Ответ от API", response.json())
                return response.json()
        except Exception as e:
            print(f"   Ошибка: {e}")
    
    # Тест 2: Получить структуру таблицы
    print("\n2️⃣ Пробуем получить структуру таблицы...")
    urls = [
        f"{MWS_API_URL}/tables/{MWS_TABLE_ID}/schema",
        f"{MWS_API_URL}/bases/{MWS_TABLE_ID}/schema",
        f"{MWS_API_URL}/tables/{MWS_TABLE_ID}/fields",
        f"{MWS_API_URL}/bases/{MWS_TABLE_ID}/fields"
    ]
    
    for url in urls:
        try:
            response = requests.get(url, headers=headers)
            print(f"   URL: {url}")
            print(f"   Статус: {response.status_code}")
            if response.status_code == 200:
                debug_print("Ответ от API", response.json())
                return response.json()
        except Exception as e:
            print(f"   Ошибка: {e}")
    
    return None

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

def test_add_record():
    """Пробует добавить тестовую запись разными способами"""
    print("\n🧪 ТЕСТИРОВАНИЕ ДОБАВЛЕНИЯ ЗАПИСИ")
    
    headers = {
        'Authorization': f'Bearer {MWS_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    test_data = {
        'match_id': 'TEST123',
        'radiant_team': 'Test Team',
        'dire_team': 'Test Team 2',
        'winner': 'Radiant',
        'duration': '45:00',
        'score': '30-25',
        'league': 'Test League',
        'had_megacreeps': 'No',
        'match_date': '2024-03-08 15:00'
    }
    
    # Пробуем разные форматы и URL
    test_cases = [
        {
            'name': 'Объект напрямую',
            'url': f"{MWS_API_URL}/tables/{MWS_TABLE_ID}/rows",
            'data': test_data
        },
        {
            'name': 'Массив с одним объектом',
            'url': f"{MWS_API_URL}/tables/{MWS_TABLE_ID}/rows",
            'data': [test_data]
        },
        {
            'name': 'Список значений',
            'url': f"{MWS_API_URL}/tables/{MWS_TABLE_ID}/rows",
            'data': list(test_data.values())
        },
        {
            'name': 'С полем records',
            'url': f"{MWS_API_URL}/tables/{MWS_TABLE_ID}/rows",
            'data': {'records': [test_data]}
        },
        {
            'name': 'С полем data',
            'url': f"{MWS_API_URL}/tables/{MWS_TABLE_ID}/rows",
            'data': {'data': [test_data]}
        },
        {
            'name': 'Пробуем другой endpoint',
            'url': f"{MWS_API_URL}/bases/{MWS_TABLE_ID}/rows",
            'data': test_data
        },
        {
            'name': 'Пробуем batch endpoint',
            'url': f"{MWS_API_URL}/tables/{MWS_TABLE_ID}/rows/batch",
            'data': [test_data]
        }
    ]
    
    for test in test_cases:
        print(f"\n📤 Тест: {test['name']}")
        print(f"URL: {test['url']}")
        print(f"Данные: {json.dumps(test['data'], ensure_ascii=False)[:200]}")
        
        try:
            response = requests.post(test['url'], headers=headers, json=test['data'])
            print(f"Статус: {response.status_code}")
            if response.status_code in [200, 201]:
                print("✅ УСПЕХ!")
                try:
                    debug_print("Ответ", response.json())
                except:
                    print("Ответ не в JSON")
            else:
                print(f"❌ Ошибка: {response.status_code}")
                try:
                    print(f"Текст ответа: {response.text[:200]}")
                except:
                    pass
        except Exception as e:
            print(f"❌ Исключение: {e}")

def main():
    print(f"🚀 Запуск отладки: {datetime.datetime.now()}")
    
    # Сначала тестируем API
    api_info = test_mws_api()
    
    # Затем пробуем добавить тестовую запись
    test_add_record()
    
    print("\n✅ Отладка завершена!")

if __name__ == "__main__":
    main()
