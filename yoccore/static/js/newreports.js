/**
 * Created by aakh on 13/03/2015.
 */

//c.post('/get_quotes2/', {'positives':'true', 'negatives':'true', 'neutrals':'true'})

function showspinner(chart_area){
	$($(chart_area).children('.chart_spinner')[0]).fadeIn(250)
}

function hidespinner(chart_area){
	$($(chart_area).children('.chart_spinner')[0]).fadeOut(250)
}

function chart_ajax_error(chart_area, msg){
	hidespinner(chart_area);
	$(chart_area).html("<div class=\"chart_ajax_error\" data-err=".concat(msg,
        ">something went wrong. Click to retry<\/div>"))
}

function clear_chart_ajax_error(chart_area){
	$(chart_area).children(".chart_ajax_error").remove()
}


function do_quote_ajax(chart_section) {

    var ca = get_chart_area(chart_section)
    $(ca).children().hide(250)
    //var endpoint = get_endpoint(ca)
    var post_data = {'positives':'true', 'negatives':'true', 'neutrals':'true'}

    clear_chart_ajax_error(ca)
    showspinner(ca)

    if (post_data == false) {
        chart_ajax_error(ca, 'post_data')
        console.log("no data, kicking out")
        return false
    }

    $.ajax({
        type: "POST",
        url: "/get_quotes2/", //default to current url
        data: post_data,

        success: function(dat) {
            quote_vis(ca, dat)
            $(ca).children().fadeIn(250)
            $(chart_section).children('chart_header').fadeIn(250)
        },
        error: function (jqXHR, exception) {
            chart_ajax_error(ca, exception);
            console.log(exception)
        },
        complete: function () {
            // submitRunning = false;
            $(ca).children().show(250)

        }
    }).done(function () {
        //console.log('ajax DONE for '.concat($(ca)) )
        return true;
    })
};