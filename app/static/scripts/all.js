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

});