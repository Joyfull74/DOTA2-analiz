import os
import requests

MWS_TOKEN = os.environ.get('MWS_TOKEN')
VIEW_ID = "viw3UUhw6Xy2w"

# Все возможные ID, которые мы видели
possible_ids = [
    "dstWj25HjQqwT4jmDC",     # из документации
    "shrdTUtqSMEl2S5URWuR7",  # из ссылки поделиться
    "viw3UUhw6Xy2w",          # view ID
    "fldkN4EjwFeEP",          # field ID
    "dstWj25HjQqwT4jmDC",     # ещё раз для проверки
]

base_url = "https://tables.mws.ru/api/v1"
headers = {
    'Authorization': f'Bearer {MWS_TOKEN}',
    'Content-Type': 'application/json'
}

print("🔍 ПОИСК ПРАВИЛЬНОГО ID ДАТАСЕТА")
print("=" * 60)

for dataset_id in possible_ids:
    url = f"{base_url}/datasets/{dataset_id}/records"
    params = {'viewId': VIEW_ID, 'fieldKey': 'id'}
    
    print(f"\n➡️ Пробуем ID: {dataset_id}")
    print(f"URL: {url}")
    
    try:
        response = requests.get(url, headers=headers, params=params)
        print(f"Статус: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Ответ: {data}")
            
            # Проверяем, есть ли данные
            if data.get('success') == True or 'data' in data:
                print(f"✅ ЭТОТ ID РАБОТАЕТ! {dataset_id}")
                break
            elif data.get('code') == 203:
                print("❌ Ресурс не существует")
        else:
            print(f"❌ Ошибка {response.status_code}")
            
    except Exception as e:
        print(f"💥 Ошибка: {e}")

print("\n✅ Поиск завершён")
