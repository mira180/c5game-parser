$(function() {
  $.getJSON('/get_conversion_rates', function(data) {
    var conversion_rates = data["conversion_rates"];
    function convert(a) {
      var val;
      if (a === 1) {
        val = parseFloat($('.converter_value.first').val()) / conversion_rates[$('.converter_currency.first').val()] * conversion_rates[$('.converter_currency.second').val()];
        val = val.toFixed(2);
        $('.converter_value.second').val(isNaN(val) ? "" : val);
      } else if (a === 2) {
        val = parseFloat($('.converter_value.second').val()) / conversion_rates[$('.converter_currency.second').val()] * conversion_rates[$('.converter_currency.first').val()];
        val = val.toFixed(2);
        $('.converter_value.first').val(isNaN(val) ? "" : val);
      }
    }
    $('.converter_value').keyup(function() {
      if ($(this).hasClass('first')) {
        convert(1);
      } else if ($(this).hasClass('second')) {
        convert(2);
      }
    });

    $('.converter_currency').change(function() {
      if ($(this).hasClass('first')) {
        convert(2);
      } else if ($(this).hasClass('second')) {
        convert(1);
      }
    })
    convert(1);
  })
})