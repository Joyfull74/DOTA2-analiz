def send_to_mws(record):
    headers = {
        'Authorization': f'Bearer {MWS_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    url = f"{API_URL}/datasets/{TABLE_ID}/records"
    params = {'viewId': VIEW_ID}
    
    try:
        print(f"📤 Отправляю данные: {record}")
        response = requests.post(url, headers=headers, params=params, json=record)
        print(f"📥 Статус: {response.status_code}")
        print(f"📥 Ответ: {response.text}")
        
        if response.status_code in [200, 201]:
            print(f"✅ Запись успешно добавлена!")
            return True
        else:
            print(f"❌ Ошибка {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Исключение: {e}")
        return False
