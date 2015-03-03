/**
 * Created by aakh on 02/03/2015.
 */

$(document).ready(function(){
    $('#the_question').fadeIn(300,function(){
        $('#the_answer').fadeIn(300, function(){
            $('#the_form').fadeIn(300);
        });
    });
});


$('.quotable').on('click', function(){
    event.preventDefault() // stops form submission
    if ($(this).hasClass('blocked')){
        console.log('blocked')
        return
    }

    $('.quotable').removeClass('picked')

    $(this).addClass('picked')
    var v = $(this).data('val')
    $('#quotable_field').val(v)

});

$('.not_fb').on('click', function(){
    event.preventDefault() // stops form submission

    $('.not_fb').removeClass('picked')

    $(this).addClass('picked')
    var v = $(this).data('val')
    $('#not_fb_field').val(v)

    if (this.id == 'not_fb'){
        $("input:radio").attr('disabled',true);
        $("select").attr('disabled',true);
        $('#quotable_field').val("false");
        $('.quotable').addClass('blocked');
        $('.quotable').prop('disabled', true);
    }
    else{
        $("input:radio").attr('disabled',false);
        $("select").attr('disabled',false);
        $('.quotable').removeClass('blocked');
        $('.quotable').prop('disabled', false);
    }

})



$('#logOut').on('click', function() {
    event.preventDefault() // stops form submission
    if ($(this).data("href")) {
        window.location = $(this).data("href");
    }
});







$('#thanks').on('click', function(){
    event.preventDefault() // stops form submission
    if ($(this).data("href")) {
        window.location = $(this).data("href");
    }
});