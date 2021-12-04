$.fn.dataTable.ext.search.push(
  function(settings, data, dataIndex) {
    var first_min_price = parseFloat($('#filter .first.min.price').val());
    var first_max_price = parseFloat($('#filter .first.max.price').val());
    var first_min_diff = parseFloat($('#filter .first.min.diff').val());
    var first_max_diff = parseFloat($('#filter .first.max.diff').val());
    var first_min_volume = parseInt($('#filter .first.min.volume').val(), 10);
    var first_max_volume = parseInt($('#filter .first.max.volume').val(), 10);
    var second_min_price = parseFloat($('#filter .second.min.price').val());
    var second_max_price = parseFloat($('#filter .second.max.price').val());
    var second_min_diff = parseFloat($('#filter .second.min.diff').val());
    var second_max_diff = parseFloat($('#filter .second.max.diff').val());
    var second_min_volume = parseInt($('#filter .second.min.volume').val(), 10);
    var second_max_volume = parseInt($('#filter .second.max.volume').val(), 10);
    var first_price = parseFloat(data[2]) || 0;
    var second_price = parseFloat(data[3]) || 0;
    var first_volume = parseInt(data[4], 10) || 0;
    var second_volume = parseInt(data[5], 10) || 0;
    var first_diff = parseFloat(data[6]) || 0;
    var second_diff = parseFloat(data[7]) || 0;
    if (!isNaN(first_min_price) && first_price < first_min_price) {
      return false
    }
    if (!isNaN(first_max_price) && first_price > first_max_price) {
      return false
    }
    if (!isNaN(first_min_diff) && first_diff < first_min_diff) {
      return false
    }
    if (!isNaN(first_max_diff) && first_diff > first_max_diff) {
      return false
    }
    if (!isNaN(first_min_volume) && first_volume < first_min_volume) {
      return false
    }
    if (!isNaN(first_max_volume) && first_volume > first_max_volume) {
      return false
    }
    if (!isNaN(second_min_price) && second_price < second_min_price) {
      return false
    }
    if (!isNaN(second_max_price) && second_price > second_max_price) {
      return false
    }
    if (!isNaN(second_min_diff) && second_diff < second_min_diff) {
      return false
    }
    if (!isNaN(second_max_diff) && second_diff > second_max_diff) {
      return false
    }
    if (!isNaN(second_min_volume) && second_volume < second_min_volume) {
      return false
    }
    if (!isNaN(second_max_volume) && second_volume > second_max_volume) {
      return false
    }
    return true
  }
);

$.fn.DataTable.ext.pager.numbers_length = 5;

$(function(){

  var table = $('#table').DataTable({
    pageLength: 100,
    columnDefs: [
      {
        targets: 1,
        orderable: false,
        searchable: false,
      },
      {
        targets: [4, 5],
        visible: false,
      }
    ],
    language: {
      emptyTable: "Нет данных в таблице",
      lengthMenu: "Показать _MENU_ предметов на странице",
      zeroRecords: "Предметов по заданному фильтру не найдено",
      search: "Поиск",
      info: "Показаны _START_-_END_ из _TOTAL_ предметов",
      infoEmpty: "Показаны 0-0 из 0 предметов",
      infoFiltered: "(по фильтру из _MAX_ предметов)",
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
    },
  });

  $('#wait_message').addClass('hidden');

  $('#filter .first, #filter .second').keyup(function() {
    table.draw();
  });

})