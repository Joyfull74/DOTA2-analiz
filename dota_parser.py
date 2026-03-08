import os
import requests
import datetime

MWS_TOKEN = os.environ.get('MWS_TOKEN')
TABLE_ID = "dstWj25HjQqwT4jmdC"
VIEW_ID = "viw3UUhw6Xy2w"

# Все возможные базовые URL
base_urls = [
    "https://tables.mws.ru/fusion/v1",
    "https://tables.mws.ru/fusion/v2",
    "https://tables.mws.ru/api/v1",
    "https://tables.mws.ru/api/v2",
    "https://tables.mws.ru/rest/v1",
    "https://tables.mws.ru/rest/v2",
    "https://api.tables.mws.ru/v1",
    "https://api.tables.mws.ru/v2",
]

# Все возможные пути для создания записи
paths = [
    f"/datasets/{TABLE_ID}/records",
    f"/datasets/{TABLE_ID}/rows",
    f"/tables/{TABLE_ID}/records",
    f"/tables/{TABLE_ID}/rows",
    f"/bases/{TABLE_ID}/records",
    f"/bases/{TABLE_ID}/rows",
]

# Тестовые данные (один матч)
test_record = {
    "fields": {
        "match_id": "12345",
        "radiant_team": "Test Team",
        "dire_team": "Test Team 2",
        "winner": "Radiant",
        "duration": "45:00",
        "score": "30-25",
        "league": "Test League",
        "had_megacreeps": "No",
        "match_date": "2024-03-08 15:00"
    }
}

print("🔍 ПОИСК РАБОЧЕГО API ENDPOINT")
print("=" * 60)

found = False
for base_url in base_urls:
    for path in paths:
        url = base_url + path
        params = {'viewId': VIEW_ID}
        headers = {
            'Authorization': f'Bearer {MWS_TOKEN}',
            'Content-Type': 'application/json'
        }
        
        print(f"\n➡️ Пробуем: {url}")
        print(f"Параметры: {params}")
        
        try:
            response = requests.post(url, headers=headers, params=params, json=test_record, timeout=10)
            print(f"Статус: {response.status_code}")
            
            if response.status_code in [200, 201]:
                print(f"✅ УСПЕХ! Найден рабочий endpoint!")
                print(f"URL: {url}")
                print(f"Ответ: {response.text[:200]}")
                found = True
                break
            elif response.status_code == 401:
                print(f"🔐 401 Unauthorized - проблема с токеном")
            elif response.status_code == 404:
                print(f"❌ 404 Not Found - путь не существует")
            else:
                print(f"⚠️ Код {response.status_code}: {response.text[:100]}")
        except Exception as e:
            print(f"💥 Ошибка соединения: {e}")
    
    if found:
        break

if not found:
    print("\n❌ НИ ОДИН ENDPOINT НЕ СРАБОТАЛ")
    print("Нужна дополнительная информация из документации MWS Tables")
