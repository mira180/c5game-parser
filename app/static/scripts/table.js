var short_names = {
  'C5GAME': 'C5',
  'STEAM': 'ST',
};

$.fn.DataTable.ext.pager.numbers_length = 5;

$(function(){

  var table = $('#table').DataTable({
    bProcessing: true,
    bServerSide: true,
    lengthMenu: [[10, 25, 50, 100], [10, 25, 50, 100]],
    sAjaxSource: '/get_table',
    fnServerParams: function ( aoData ) {
      aoData.push( { "name": "first_platform", "value": $('#filter .first.platform').val() },
                   { "name": "second_platform", "value": $('#filter .second.platform').val() },
                   { "name": "first_min_price", "value": $('#filter .first.min.price').val() },
                   { "name": "first_max_price", "value": $('#filter .first.max.price').val() },
                   { "name": "first_min_diff", "value": $('#filter .first.min.diff').val() },
                   { "name": "first_max_diff", "value": $('#filter .first.max.diff').val() },
                   { "name": "first_min_volume", "value": $('#filter .first.min.volume').val() },
                   { "name": "first_max_volume", "value": $('#filter .first.max.volume').val() },
                   { "name": "first_autobuy", "value": $('#filter .first.autobuy').is(':checked') },
                   { "name": "second_min_price", "value": $('#filter .second.min.price').val() },
                   { "name": "second_max_price", "value": $('#filter .second.max.price').val() },
                   { "name": "second_min_diff", "value": $('#filter .second.min.diff').val() },
                   { "name": "second_max_diff", "value": $('#filter .second.max.diff').val() },
                   { "name": "second_min_volume", "value": $('#filter .second.min.volume').val() },
                   { "name": "second_max_volume", "value": $('#filter .second.max.volume').val() },
                   { "name": "second_autobuy", "value": $('#filter .second.autobuy').is(':checked') },
                   { "name": "game", "value": $('#table').data('game') }
                   )
    },   
    columns: [
      {"data": "Название предмета"},
      {"data": "Платформы"},
      {"data": "Первая цена"},
      {"data": "Вторая цена"},
      {"data": "Первая разница"},
      {"data": "Вторая разница"},
    ],
    order: [[4, 'desc']],
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
      $(table.column(2).header()).text(short_names[$('#filter .first.platform').val()])
      $(table.column(3).header()).text(short_names[$('#filter .second.platform').val()])
      $(table.column(4).header()).text(short_names[$('#filter .first.platform').val()] + '->' + short_names[$('#filter .second.platform').val()])
      $(table.column(5).header()).text(short_names[$('#filter .second.platform').val()] + '->' + short_names[$('#filter .first.platform').val()])
      $('.ui.sticky')
        .sticky('refresh')
      ;
    }
  });

  $('#filter .first, #filter .second').keyup(function() {
    $('#filter .row.apply').show();
    //table.draw();
  });

  $('#filter .first.platform, #filter .second.platform, #filter .first.autobuy, #filter .second.autobuy').change(function() {
    $('#filter .row.apply').show();
    //table.draw();
  })

  $('#filter .row.apply button').click(function() {
    table.draw();
    $('#filter .row.apply').hide();
  })

})