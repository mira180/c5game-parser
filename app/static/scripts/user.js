$(function() {
  var steam_id = $('#user_profile').data('steam_id');

  toastr.options = {
    "closeButton": false,
    "debug": false,
    "newestOnTop": false,
    "progressBar": true,
    "positionClass": "toast-bottom-center",
    "preventDuplicates": false,
    "onclick": null,
    "showDuration": "300",
    "hideDuration": "1000",
    "timeOut": "5000",
    "extendedTimeOut": "1000",
    "showEasing": "swing",
    "hideEasing": "linear",
    "showMethod": "fadeIn",
    "hideMethod": "fadeOut"
  };
  
  $('#give_sub').click(function() {
    toastr["success"]("Подписка выдана (+30 дней)");
    $.get("/admin/control", {'op': 'give_sub', 'steam_id': steam_id});
  });

  $('#take_sub').click(function() {
    toastr["warning"]("Подписка удалена");
    $.get("/admin/control", {'op': 'take_sub', 'steam_id': steam_id});
  })
});