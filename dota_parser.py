import os
import requests

MWS_TOKEN = os.environ.get('MWS_TOKEN')
BASE_URL = "https://tables.mws.ru/api/v1"
VIEW_ID = "viw3UUhw6Xy2w"

# Список ID для проверки (добавим еще один из вашей ссылки на запись)
ids_to_try = [
    "dstWj25HjQqwT4jmdC",  # из основного URL
    "viw3UUhw6Xy2w",       # ID представления
    "shrdTUtqSMEl2S5URWuR7", # из ссылки "Поделиться"
    "recul0FclA6MW",       # ID конкретной записи (только что скопировали)
    "fldkN4EjwFeEP",       # Field ID
]

headers = {'Authorization': f'Bearer {MWS_TOKEN}'}
params = {'viewId': VIEW_ID}

print("🔍 ПОИСК ПРАВИЛЬНОГО ID ДАТАСЕТА")
print("=" * 60)

for test_id in ids_to_try:
    url = f"{BASE_URL}/datasets/{test_id}/records"
    print(f"\n➡️ Пробуем ID: {test_id}")
    print(f"URL: {url}")
    
    try:
        # Пробуем просто получить информацию (GET), чтобы проверить существование
        response = requests.get(url, headers=headers, params=params)
        print(f"Статус GET: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Ответ: {data}")
            if data.get('success') is True or 'data' in data:
                print(f"✅ РАБОЧИЙ ID НАЙДЕН: {test_id}")
                break
            elif data.get('code') == 203:
                print(f"⏩ ID {test_id} не подходит (ресурс не существует)")
    except Exception as e:
        print(f"💥 Ошибка: {e}")

print("\n✅ Поиск завершён")
