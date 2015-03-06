/**
 * Created by aakh on 04/03/2015.
 */


function get_colour_for_branch(branch){
    if (branch=='moorgate'||branch=='m'||branch=='Moorgate'||branch=='M') {
        return '#211E31'
    }
    else {
        return '#666666'
    }
}

function split_string_by_pipe(str, delim){
    var result = [];

    if (delim==null){ delim = "|"};

    str.split(delim).forEach(function(x){
        result.push(x)
    });

    return result
}

function get_chart_section_for_chart_section_toggle(ele){
	return $(ele).parent().parent()
}



function get_chart_area(chart_section){
	return $(chart_section).find('.chart_area')[0]
};

function showspinner(chart_area){
	$($(chart_area).children('.chart_ajax_error')[0]).fadeIn(250)
}

function hidespinner(chart_area){
	$($(chart_area).children('.chart_ajax_error')[0]).fadeOut(250)
}

function chart_ajax_error(chart_area, msg){
	hidespinner(chart_area);
	$(chart_area).html("<div class=\"chart_ajax_error\" data-err=".concat(msg,
        ">something went wrong. Click to retry<\/div>"))
}

function clear_chart_ajax_error(chart_area){
	$(chart_area).children(".chart_ajax_error").remove()
}

function extract_quote(chart_area, dat){
    var ca = $(chart_area);
    var pos_list = dat['positive_quotes'];
    var neg_list = dat['negative_quotes'];

    var pos_ul_open = "<ul class=\"quoteitem\">"
    var neg_ul_open = "<ul class=\"quoteitem2\">"
    var ul_open2 = "<ul class=\"quoteitem3\">"
    var ul_close = "<\/ul>"

    var pos_div = "<div class=\"col-4-10 quotes big-bottom-margin pos\">"
    for (i=0; i<pos_list.length; i++){
        pos_div = pos_div.concat(pos_ul_open,pos_list[i].quote, ul_close)

        if (pos_list[i].age && pos_list[i].gender){
            pos_div = pos_div.concat(ul_open2,pos_list[i].age,', ', pos_list[i].gender, ul_close)
        }
    }
    pos_div = pos_div.concat("<\/div>")

    var neg_div = "<div class=\"col-4-10 quotes big-top-margin neg\">"
    for (i=0; i<neg_list.length; i++){
        neg_div = neg_div.concat(neg_ul_open,neg_list[i].quote, ul_close)

        if (neg_list[i].age && neg_list[i].gender){
            neg_div = neg_div.concat(ul_open2,neg_list[i].age,', ', neg_list[i].gender, ul_close)
        }
    }
    neg_div = neg_div.concat("<\/div>")


    ca.html(pos_div.concat(neg_div))
}

function nvd3chart(chart_area, dat){
    var ca = $(chart_area)
    var ca_svg = ca.children('svg')[0]
    nv.addGraph(function() {


        var chart = nv.models.multiBarChart()
            .color(d3.scale.category10().range())
            .reduceXTicks(false)   //If 'false', every single x-axis tick label will be rendered.
            .rotateLabels(90)      //Angle to rotate x-axis labels.
            .showControls(true)   //Allow user to switch between 'Grouped' and 'Stacked' mode.
            .groupSpacing(0.1)    //Distance between each group of bars.

    ;

    chart.xAxis
        .tickFormat(function(d){
            return d3.time.format('%d-%b')(new Date(d))//(new Date(d))
        });

    chart.yAxis
        .tickFormat(d3.format(',.1f'));

    d3.select(ca_svg)
        .datum(dat)
        .call(chart);

    nv.utils.windowResize(chart.update);

    return chart;
});
}

function get_vis(chart_area, dat){
    ca = $(chart_area)
    console.log('get vis'.concat(ca))
    console.log(dat)
    if (dat == null){
        chart_ajax_error(chart_area, 'null')
    }else{

        if (ca.data('series') == 'branch' ||
                ca.data('series') == 'gender' ||
                //ca.data('series') == 'rating' ||
                ca.data('series') == 'age'){

            nvd3chart(chart_area, dat)

        }
        else if (ca.data('series') == 'quote'){
            extract_quote(chart_area, dat)
        }
        else if(ca.data('series') == 'app_names'){
            ca.html("success")
        }
        else if(ca.data('series') == 'app_feedback'){
            ca.html("success")
        }
        else {
            chart_ajax_error(chart_area, 'series')
        }


        hidespinner(chart_area)

    }
}

function get_endpoint(chart_area){
    var report_num = {}
    report_num['intf'] = $(chart_area).data("report_num")

    $.ajax({
        type: "POST",
        url: "/get_report_url/",
        data: report_num,

        success: function (dat) {
            console.log(dat)
            return dat
        },
        error: function (jqXHR, exception) {
            return false
        },
        complete: function (jqXHR, textStatus) {
            // submitRunning = false;
            console.log('get_endpoint complete for '.concat(chart_area, textStatus) )
        }
    }).done(function () {
            // submitRunning = false;
            console.log('get_endpoint DONE for '.concat(chart_area) )
        })
}

function get_post_data(chart_area){
    var ca = $(chart_area);
    var data = {};
    data['desired_series'] = ca.data("series");
    data['desired_filters'] = {};
    data['intf'] = $(chart_area).data("report_num")

    return data
}


function do_chart_ajax(chart_section) {

    var ca = get_chart_area(chart_section)
    //var endpoint = get_endpoint(ca)
    var post_data = get_post_data(ca) //todo!

    clear_chart_ajax_error(ca)
    showspinner(ca)

    //if (endpoint == false) {
    //    chart_ajax_error(ca, 'get_endpoint')
    //    console.log("no enpoint, kicking out")
    //    return false
    //}

    if (post_data == false) {
        chart_ajax_error(ca, 'post_data')
        console.log("no data, kicking out")
        return false
    }

    $.ajax({
        type: "POST",
        //url: endpoint, //default to current url
        data: post_data,

        success: function(dat) {
            get_vis(ca, dat)
        },
        error: function (jqXHR, exception) {
            chart_ajax_error(ca, exception);
            console.log(exception)
        },
        complete: function () {
            // submitRunning = false;

        }
    }).done(function () {
        console.log('ajax DONE for '.concat($(ca)) )
        return true;
    })
};



$('.chart_section_toggle').on('click', function(){
	var ele = $(this);
	var chart_section = get_chart_section_for_chart_section_toggle(ele);
    do_chart_ajax(chart_section)
});

$('.refresh_chart').on('click', function(){
    var t = $($(this)[0]).parent().parent() //todo:change to get_chart_section
    do_chart_ajax($(t))
})

$(document).ready(function(){
    var chart_sections = $('.chart_section')

    for (i = 0; i <  chart_sections.length; i++){
		console.log('loop'.concat(i))
        var chart_section = chart_sections[i]
        do_chart_ajax($(chart_section))
    }


});
