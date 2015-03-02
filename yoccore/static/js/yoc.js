/**
 * Created by aakh on 02/03/2015.
 */

$(document).ready(function(){
    $('#the_question').fadeIn(250,function(){
        $('#the_answer').fadeIn(250);
        $('#the_form').fadeIn(250);
    });
})


$('.quotable').on('click', function(){
    event.preventDefault() // stops form submission
    $('.quotable').removeClass('picked')

    $(this).addClass('picked')
    var v = $(this).data('val')
    $('#quotable_field').val(v)

})


$('#logOut').on('click', function() {
    event.preventDefault() // stops form submission
    if ($(this).data("href")) {
        window.location = $(this).data("href");
    }
});

$('#nf').on('click', function () {
    if (this.checked){
        $("input:radio").attr('disabled',true);
        $("select").attr('disabled',true);
        $('#quotable_field').val("")
        $('.quotable').removeClass('picked')
    }
    else{
        $("input:radio").attr('disabled',false);
        $("select").attr('disabled',false);
    }
}
)
