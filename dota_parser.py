import os
import requests

MWS_TOKEN = os.environ.get('MWS_TOKEN')
DATASET_ID = "dstWj25HjQqwT4jmDC"
VIEW_ID = "viw3UUhw6Xy2w"

# Все возможные базовые URL
base_urls = [
    "https://tables.mws.ru/api",
    "https://tables.mws.ru/api/v1",
    "https://tables.mws.ru/rest",
    "https://tables.mws.ru/rest/v1",
    "https://tables.mws.ru/v1",
    "https://tables.mws.ru/fusion/api",
    "https://tables.mws.ru/fusion/rest",
    "https://api.tables.mws.ru",
    "https://api.tables.mws.ru/v1",
]

# Все возможные пути
paths = [
    f"/datasets/{DATASET_ID}/records",
    f"/tables/{DATASET_ID}/rows",
    f"/bases/{DATASET_ID}/records",
    f"/records/{DATASET_ID}",
]

headers = {
    'Authorization': f'Bearer {MWS_TOKEN}',
    'Content-Type': 'application/json'
}

# Тестовые данные
test_data = {"records": [{"fields": {"fldkN4EjwFeEP": "test"}}]}

print("🔍 ПОИСК РАБОЧЕГО API ENDPOINT")
print("=" * 60)

found = False
for base in base_urls:
    for path in paths:
        url = base + path
        full_url = f"{url}?viewId={VIEW_ID}&fieldKey=id"
        
        try:
            print(f"➡️ Пробуем: {full_url}")
            response = requests.post(full_url, headers=headers, json=test_data, timeout=5)
            
            if response.status_code == 200:
                print(f"✅ НАЙДЕН! 200 OK: {full_url}")
                print(f"Ответ: {response.text[:200]}")
                found = True
                break
            elif response.status_code == 201:
                print(f"✅ НАЙДЕН! 201 Created: {full_url}")
                print(f"Ответ: {response.text[:200]}")
                found = True
                break
            elif response.status_code == 401:
                print(f"🔐 401 Unauthorized (токен не подходит): {full_url}")
            elif response.status_code == 404:
                print(f"❌ 404 Not Found: {full_url}")
            else:
                print(f"⚠️ {response.status_code}: {full_url}")
        except Exception as e:
            print(f"💥 Ошибка соединения: {full_url} - {e}")
    
    if found:
        break

if not found:
    print("\n❌ НИЧЕГО НЕ НАЙДЕНО")
    print("Нужно смотреть реальные запросы в браузере (F12 → Network)")
