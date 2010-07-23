
function moduleForm(event) {
   args = $(this).serialize();
   args['page_modules'] = $('.module').map(function() { return this.id; }).get().join(',');
   $.post($(this).attr('action'), args,
          function(result) {
             result = eval(result);
             for (var i=0; i<result.length; i++) {
                var widget = result[i];
                $("#"+$(widget).attr('id')).replaceWith(widget);
             }
             attach();
             // reset form?
          });
   event.preventDefault();
   return false;
}

function moduleAction(event) {
   $.post($(this).attr('href'),
          { 'page_modules': $('.module').map(function() { return this.id; }).get().join(',') },
          function(result) {
             //alert("got result=" + result);
             result = eval(result);
             for (var i=0; i<result.length; i++) {
                var widget = result[i];
                $("#"+$(widget).attr('id')).replaceWith(widget);
             }
             attach();
          });
   event.preventDefault();
   return false;
}

function attach() {
   $('.module-action').click(moduleAction);
   $('form.module-form').submit(moduleForm);
}

$(document).ready(function() {
   attach();
});
