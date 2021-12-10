$.fn.DataTable.ext.pager.numbers_length = 5;

$(function(){

  $('#orders_table').DataTable({
    bProcessing: true,
    bServerSide: true,
    lengthMenu: [[10, 25, 50, 100], [10, 25, 50, 100]],
    sAjaxSource: '/admin/get_orders',
    columns: [
      {"data": "Пользователь", "sortable": false},
      {"data": "Номер заказа"},
      {"data": "Дата создания"},
      {"data": "Сумма"},
      {"data": "Статус"}
    ],
    order: [[ 1, 'desc' ]],
    language: {
      emptyTable: "Нет данных в таблице",
      lengthMenu: "Показать _MENU_ операций на странице",
      zeroRecords: "Операций по заданному фильтру не найдено",
      search: "Поиск",
      info: "Показаны _START_-_END_ из _TOTAL_ операций",
      infoEmpty: "Показаны 0-0 из 0 операций",
      infoFiltered: "(по фильтру из _MAX_ операций)",
      loadingRecords: "Загрузка...",
      processing: "Обработка...",
      paginate: {
        first: "В начало",
        last: "В конец",
        next: "Вперед",
        previous: "Назад"
      },
      "aria": {
        sortAscending:  ": сортировать по возрастанию",
        sortDescending: ": сортировать по убыванию"
      }
    },
    drawCallback: function() {
      $('.ui.sticky')
        .sticky('refresh')
      ;
    }
  });

  $('#users_table').DataTable({
    bProcessing: true,
    bServerSide: true,
    lengthMenu: [[10, 25, 50, 100], [10, 25, 50, 100]],
    sAjaxSource: '/admin/get_users',
    columns: [
      {"data": "Пользователь", "sortable": false},
      {"data": "Подписка"},
      {"data": "Подписка истекает", "sortable": false},
      {"data": "Дата регистрации"},
      {"data": "Последний визит"}
    ],
    order: [[ 3, 'desc' ]],
    language: {
      emptyTable: "Нет данных в таблице",
      lengthMenu: "Показать _MENU_ пользователей на странице",
      zeroRecords: "Пользователей по заданному фильтру не найдено",
      search: "Поиск",
      info: "Показаны _START_-_END_ из _TOTAL_ пользователей",
      infoEmpty: "Показаны 0-0 из 0 пользователей",
      infoFiltered: "(по фильтру из _MAX_ пользователей)",
      loadingRecords: "Загрузка...",
      processing: "Обработка...",
      paginate: {
        first: "В начало",
        last: "В конец",
        next: "Вперед",
        previous: "Назад"
      },
      "aria": {
        sortAscending:  ": сортировать по возрастанию",
        sortDescending: ": сортировать по убыванию"
      }
    },
    drawCallback: function() {
      $('.ui.sticky')
        .sticky('refresh')
      ;
    }
  });

})