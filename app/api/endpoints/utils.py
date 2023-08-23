SUM_ALL_ITEMS = 'Выдача списка {}'
SUM_ITEM = 'Возвращает {} по ID'
SUM_CREATE_ITEM = 'Создание нового {}'
SUM_UPDATE_ITEM = 'Редактирование {}'
SUM_DELETE_ITEM = 'Удаление {}'


def delete_response(item_name: str) -> str:
    return {'status': True, 'message': f'The {item_name} has been deleted'}
