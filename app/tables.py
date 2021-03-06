from flask import current_app
import re
from constants import price_re
from datetime import datetime

class ServerSideTable(object):
    '''
    Retrieves the values specified by Datatables in the request and processes
    the data that will be displayed in the table (filtering, sorting and
    selecting a subset of it).

    Attributes:
        request: Values specified by DataTables in the request.
        data: Data to be displayed in the table.
        column_list: Schema of the table that will be built. It contains
                     the name of each column (both in the data and in the
                     table), the default values (if available) and the
                     order in the HTML.
    '''
    def __init__(self, request, data, column_list):
        self.result_data = None
        self.cardinality_filtered = 0
        self.cardinality = 0

        self.request_values = request.values
        self.columns = sorted(column_list, key=lambda col: col['order'])

        rows = self._extract_rows_from_data(data)
        self._run(rows)

    def _run(self, data):
        '''
        Prepares the data, and values that will be generated as output.
        It does the actual filtering, sorting and paging of the data.

        Args:
            data: Data to be displayed by DataTables.
        '''
        self.cardinality = len(data)                       # Total num. of rows

        filtered_data = self._custom_filter(data)
        self.cardinality_filtered = len(filtered_data)    # Num. displayed rows

        sorted_data = self._custom_sort(filtered_data)
        self.result_data = self._custom_paging(sorted_data)

    def _extract_rows_from_data(self, data):
        '''
        Extracts the value of each column from the original data using the
        schema of the table.

        Args:
            data: Data to be displayed by DataTables.

        Returns:
            List of dicts that represents the table's rows.
        '''
        rows = []
        for x in data:
            row = {}
            for column in self.columns:
                default = column['default']
                data_name = column['data_name']
                column_name = column['column_name']
                row[column_name] = x.get(data_name, default)
            rows.append(row)
        return rows

    def _custom_filter(self, data):
        '''
        Filters out those rows that do not contain the values specified by the
        user using a case-insensitive regular expression.

        It takes into account only those columns that are 'searchable'.

        Args:
            data: Data to be displayed by DataTables.

        Returns:
            Filtered data.
        '''
        def check_row(row):
            ''' Checks whether a row should be displayed or not. '''
            for i in range(len(self.columns)):
                if self.columns[i]['searchable']:
                    value = row[self.columns[i]['column_name']]
                    regex = '(?i)' + self.request_values['sSearch']
                    if re.compile(regex).search(str(value)):
                        return True
            return False

        if self.request_values.get('sSearch', ""):
            return [row for row in data if check_row(row)]
        else:
            return data

    def _custom_sort(self, data):
        '''
        Sorts the rows taking in to account the column (or columns) that the
        user has selected.

        Args:
            data: Filtered data.

        Returns:
            Sorted data by the columns specified by the user.
        '''
        def is_reverse(str_direction):
            ''' Maps the 'desc' and 'asc' words to True or False. '''
            return True if str_direction == 'desc' else False

        if (self.request_values['iSortCol_0'] != "") and (int(self.request_values['iSortingCols']) > 0):
            for i in range(0, int(self.request_values['iSortingCols'])):
                column_number = int(self.request_values['iSortCol_' + str(i)])
                column_name = self.columns[column_number]['column_name']
                sort_direction = self.request_values['sSortDir_' + str(i)]
                if column_name in ["???????????? ????????", "???????????? ????????"]:
                    data = sorted(data,
                                key=lambda x: float(price_re.search(x[column_name]).group(1).replace('$', '')),
                                reverse=is_reverse(sort_direction))
                elif column_name in ["???????????? ??????????????", "???????????? ??????????????", "??????????"]:
                    data = sorted(data,
                                key=lambda x: float(re.sub('[$%]', '', x[column_name])),
                                reverse=is_reverse(sort_direction))
                elif column_name in ["???????? ????????????????", "???????? ??????????????????????", "?????????????????? ??????????"]:
                    data = sorted(data,
                                key=lambda x: datetime.strptime(x[column_name], current_app.config['DATE_FORMAT']),
                                reverse=is_reverse(sort_direction))
                else:
                    data = sorted(data,
                                key=lambda x: x[column_name],
                                reverse=is_reverse(sort_direction))

            return data
        else:
            return data

    def _custom_paging(self, data):
        '''
        Selects a subset of the filtered and sorted data based on if the table
        has pagination, the current page and the size of each page.

        Args:
            data: Filtered and sorted data.

        Returns:
            Subset of the filtered and sorted data that will be displayed by
            the DataTables if the pagination is enabled.
        '''
        def requires_pagination():
            ''' Check if the table is going to be paginated '''
            if self.request_values['iDisplayStart'] != "":
                if int(self.request_values['iDisplayLength']) != -1:
                    return True
            return False

        if not requires_pagination():
            return data

        start = int(self.request_values['iDisplayStart'])
        length = int(self.request_values['iDisplayLength'])

        # if search returns only one page
        if len(data) <= length:
            # display only one page
            return data[start:]
        else:
            limit = -len(data) + start + length
            if limit < 0:
                # display pagination
                return data[start:limit]
            else:
                # display last page of pagination
                return data[start:]

    def output_result(self):
        '''
        Generates a dict with the content of the response. It contains the
        required values by DataTables (echo of the reponse and cardinality
        values) and the data that will be displayed.

        Return:
            Content of the response.
        '''
        output = {}
        output['sEcho'] = str(int(self.request_values['sEcho']))
        output['iTotalRecords'] = str(self.cardinality)
        output['iTotalDisplayRecords'] = str(self.cardinality_filtered)
        output['data'] = self.result_data
        return output

class TableBuilder(object):

    def __init__(self, columns):
        self.columns = columns

    def collect_data_clientside(self, data):
        return {'data': data}

    def collect_data_serverside(self, request, data):
        return ServerSideTable(request, data, self.columns).output_result()

ITEMS_TABLE_COLUMNS = [
    {
        "data_name": "name",
        "column_name": "???????????????? ????????????????",
        "default": "",
        "order": 1,
        "searchable": True
    },
    {
        "data_name": "platforms",
        "column_name": "??????????????????",
        "default": "",
        "order": 2,
        "searchable": False
    },
    {
        "data_name": "first_price",
        "column_name": "???????????? ????????",
        "default": 0,
        "order": 3,
        "searchable": False
    },
    {
        "data_name": "second_price",
        "column_name": "???????????? ????????",
        "default": 0,
        "order": 4,
        "searchable": False
    },
    {
        "data_name": "first_diff",
        "column_name": "???????????? ??????????????",
        "default": 0,
        "order": 5,
        "searchable": False
    },
    {
        "data_name": "second_diff",
        "column_name": "???????????? ??????????????",
        "default": 0,
        "order": 6,
        "searchable": False
    }
]

ORDERS_TABLE_COLUMNS = [
    {
        "data_name": "user",
        "column_name": "????????????????????????",
        "default": "",
        "order": 1,
        "searchable": True
    },
    {
        "data_name": "order_id",
        "column_name": "?????????? ????????????",
        "default": "",
        "order": 2,
        "searchable": True
    },
    {
        "data_name": "created",
        "column_name": "???????? ????????????????",
        "default": "",
        "order": 3,
        "searchable": True
    },
    {
        "data_name": "amount",
        "column_name": "??????????",
        "default": "",
        "order": 4,
        "searchable": True
    },
    {
        "data_name": "status",
        "column_name": "????????????",
        "default": "",
        "order": 5,
        "searchable": True
    }
]

USERS_TABLE_COLUMNS = [
    {
        "data_name": "user",
        "column_name": "????????????????????????",
        "default": "",
        "order": 1,
        "searchable": True
    },
    {
        "data_name": "subscribed",
        "column_name": "????????????????",
        "default": "",
        "order": 2,
        "searchable": True
    },
    {
        "data_name": "expires",
        "column_name": "???????????????? ????????????????",
        "default": "",
        "order": 3,
        "searchable": True
    },
    {
        "data_name": "registered",
        "column_name": "???????? ??????????????????????",
        "default": "",
        "order": 4,
        "searchable": True
    },
    {
        "data_name": "last_seen",
        "column_name": "?????????????????? ??????????",
        "default": "",
        "order": 5,
        "searchable": True
    }
]