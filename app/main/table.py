from serverside_table import ServerSideTable

SERVERSIDE_TABLE_COLUMNS = [
    {
        "data_name": "name",
        "column_name": "Название предмета",
        "default": "",
        "order": 1,
        "searchable": True
    },
    {
        "data_name": "platforms",
        "column_name": "Платформы",
        "default": "",
        "order": 2,
        "searchable": False
    },
    {
        "data_name": "first_price",
        "column_name": "Первая цена",
        "default": 0,
        "order": 3,
        "searchable": False
    },
    {
        "data_name": "second_price",
        "column_name": "Вторая цена",
        "default": 0,
        "order": 4,
        "searchable": False
    },
    {
        "data_name": "first_diff",
        "column_name": "Первая разница",
        "default": 0,
        "order": 5,
        "searchable": False
    },
    {
        "data_name": "second_diff",
        "column_name": "Вторая разница",
        "default": 0,
        "order": 6,
        "searchable": False
    }
]

class TableBuilder(object):

    def collect_data_clientside(self, data):
        return {'data': data}

    def collect_data_serverside(self, request, data):
        columns = SERVERSIDE_TABLE_COLUMNS
        return ServerSideTable(request, data, columns).output_result()