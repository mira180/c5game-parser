$(function() {
  $('#payment .months').keypress(function (event) {
    if (event.which !== 8 && event.which !== 0 && event.which < 48 || event.which > 57) {
      return false
    }
  });

  $('#payment .months').keyup(function (event) {
    $('#payment .sum').text($(this).val() * 5.0 + '$')
  });
})