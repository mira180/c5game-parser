$(function(){

    $('.ui.sticky')
      .sticky({
        context: '.main.container',
        offset: 30
      })
    ;

    $('.ui.accordion')
      .accordion({
        'exclusive': false,
        onChange: function() {
          $('.ui.sticky')
            .sticky('refresh')
          ;
        }
      })
    ;

    $('#toc').sidebar({'transition': 'overlay'})

    $('#open_sidebar')
      .click(function(){
        $('#toc').sidebar('toggle')
      })
    ;

    $('.ui.dropdown')
      .dropdown()
    ;

    $('#months').keypress(function (event) {
      if (event.which !== 8 && event.which !== 0 && event.which < 48 || event.which > 57) {
        return false
      }
    });

    $('#months').keyup(function (event) {
      $('#sum').text($(this).val() * 5 + '$')
    });

});