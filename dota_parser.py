def send_to_mws(record, match_id):
    """Отправляет запись в MWS Tables"""
    
    headers = {
        'Authorization': f'Bearer {MWS_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    # Сначала создаём пустую запись
    create_url = f"{API_URL}/datasets/{TABLE_ID}/records"
    params = {'viewId': VIEW_ID}
    
    print(f"\n📤 Создание записи для матча {match_id}...")
    
    # Создаём пустую запись
    create_response = requests.post(create_url, headers=headers, params=params, json={})
    print(f"📥 Статус создания: {create_response.status_code}")
    print(f"📥 Ответ создания: {create_response.text}")
    
    if create_response.status_code not in [200, 201]:
        print("❌ Не удалось создать запись")
        return False
    
    # Из ответа получаем ID новой записи
    try:
        response_data = create_response.json()
        record_id = response_data.get('data', {}).get('id')
        if not record_id:
            print("❌ Не получен ID записи")
            return False
    except:
        print("❌ Ошибка парсинга ответа")
        return False
    
    # Теперь обновляем созданную запись с данными
    update_url = f"{API_URL}/datasets/{TABLE_ID}/records/{record_id}"
    print(f"📤 Обновление записи {record_id}...")
    
    update_response = requests.patch(update_url, headers=headers, params=params, json=record)
    print(f"📥 Статус обновления: {update_response.status_code}")
    print(f"📥 Ответ обновления: {update_response.text}")
    
    if update_response.status_code in [200, 201]:
        print(f"✅ Успешно!")
        return True
    else:
        print(f"❌ Ошибка обновления")
        return False
