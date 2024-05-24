def get_pagination(request, count_records):
    object_pagination = {
        'current_page': 1,
        'limit_items': 8
    }

    page = request.GET.get('page')
    if page:
        object_pagination['current_page'] = int(page)

    object_pagination['skip'] = (object_pagination['current_page'] - 1) * object_pagination['limit_items']
    object_pagination['total_page'] = (count_records + object_pagination['limit_items'] - 1) // object_pagination['limit_items']

    return object_pagination

def get_pagination_home(request, count_records):
    object_pagination = {
        'current_page': 1,
        'limit_items': 16
    }

    page = request.GET.get('page')
    if page:
        object_pagination['current_page'] = int(page)

    object_pagination['skip'] = (object_pagination['current_page'] - 1) * object_pagination['limit_items']
    object_pagination['total_page'] = (count_records + object_pagination['limit_items'] - 1) // object_pagination['limit_items']

    return object_pagination