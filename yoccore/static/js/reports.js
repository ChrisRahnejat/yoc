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

function extract_app_feedback(chart_area, dat){
    var ca = $(chart_area);
    var mm_list = split_string_by_pipe(dat['mm']);
    var hm_list = split_string_by_pipe(dat['hm']);
    var sp_list = split_string_by_pipe(dat['sp']);
    var gen_list = split_string_by_pipe(dat['general']);

    var pos_ul_open = "<ul class=\"quoteitem4\">";
    var pos_ul_open_b = "<ul class=\"quoteitem4b\">";
    //var pos_ul_open_close =    "em\">";
    var ul_close = "<\/ul>";

    var mm_div = "<div class=\"col-1-4 quotes pos\"><div>Manage Money</div>";
    var sp_div = "<div class=\"col-1-4 quotes neg\"><div>Spenderorama</div>";
    var hm_div = "<div class=\"col-1-4 quotes pos\"><div>House Move</div>";
    var gen_div = "<div class=\"col-1-4 quotes neg\"><div>General</div>";

    for (m1=0; m1<mm_list.length; m1++){
        mm_div = mm_div.concat(pos_ul_open, mm_list[m1], ul_close);
    }
    mm_div = mm_div.concat("<\/div>");

    for (m1=0; m1<sp_list.length; m1++){
        sp_div = sp_div.concat(pos_ul_open_b, sp_list[m1], ul_close);
    }
    sp_div = sp_div.concat("<\/div>");

    for (m1=0; m1<hm_list.length; m1++){
        hm_div = hm_div.concat(pos_ul_open, hm_list[m1], ul_close);
    }
    hm_div = hm_div.concat("<\/div>");

    for (m1=0; m1<gen_list.length; m1++){
        gen_div = gen_div.concat(pos_ul_open_b, gen_list[m1], ul_close);
    }
    gen_div = gen_div.concat("<\/div>");

    ca.html(mm_div.concat(sp_div).concat(hm_div).concat(gen_div))
}

function extract_app_names(chart_area, dat){
    var ca = $(chart_area);
    var mm_list = dat['mm'];
    var hm_list = dat['hm'];
    var sp_list = dat['sp'];

    var pos_ul_open = "<ul class=\"quoteitem4\" style=\"font-size:";
    var pos_ul_open_close =    "em\">";
    var ul_close = "<\/ul>";

    var mm_div = "<div class=\"col-1-3 quotes pos\"><div>Manage Money</div>";
    for (var key in mm_list){
        mm_div = mm_div.concat(pos_ul_open,mm_list[key],pos_ul_open_close,key, ul_close);
    }
    mm_div = mm_div.concat("<\/div>");

    var pos_ul_open_b = "<ul class=\"quoteitem4b\" style=\"font-size:";
    var sp_div = "<div class=\"col-1-3 quotes neg\"><div>Spenderorama</div>";
    for (var key2 in sp_list){
        sp_div = sp_div.concat(pos_ul_open_b,sp_list[key2],pos_ul_open_close,key2, ul_close)
    }
    sp_div = sp_div.concat("<\/div>");

    var hm_div = "<div class=\"col-1-3 quotes pos\"><div>House Move</div>";
    for (var key3 in hm_list){
        hm_div = hm_div.concat(pos_ul_open,hm_list[key3],pos_ul_open_close,key3, ul_close)
    }
    hm_div = hm_div.concat("<\/div>");

    ca.html(mm_div.concat(sp_div).concat(hm_div))

}

function extract_quote(chart_area, dat){
    var ca = $(chart_area);
    var pos_list = dat['positive_quotes'];
    var neg_list = dat['negative_quotes'];

    var pos_ul_open = "<ul class=\"quoteitem\">"
    var neg_ul_open = "<ul class=\"quoteitem2\">"
    var ul_open2 = "<ul class=\"quoteitem3\">"
    var ul_close = "<\/ul>"

    var pos_div = "<div class=\"col-4-10 quotes big-bottom-margin pos\"><div>Positive</div>"
    for (i=0; i<pos_list.length; i++){
        pos_div = pos_div.concat(pos_ul_open,pos_list[i].quote, ul_close)

        if (pos_list[i].age && pos_list[i].gender){
            pos_div = pos_div.concat(ul_open2,pos_list[i].age,', ', pos_list[i].gender, ul_close)
        }
    }
    pos_div = pos_div.concat("<\/div>")

    var neg_div = "<div class=\"col-4-10 quotes big-top-margin neg\"><div>Negative</div>"
    for (i=0; i<neg_list.length; i++){
        neg_div = neg_div.concat(neg_ul_open,neg_list[i].quote, ul_close)

        if (neg_list[i].age && neg_list[i].gender){
            neg_div = neg_div.concat(ul_open2,neg_list[i].age,', ', neg_list[i].gender, ul_close)
        }
    }
    neg_div = neg_div.concat("<\/div>")


    ca.html(pos_div.concat(neg_div))
}

function nvd3chart(chart_area, dat, y_axis_label){
    var ca = $(chart_area)
    var ca_svg = ca.children('svg')[0]
    nv.addGraph(function() {


        var chart = nv.models.multiBarChart()
            .color(d3.scale.category10().range())
            .margin({left: 100})
            .reduceXTicks(false)   //If 'false', every single x-axis tick label will be rendered.
            // .rotateLabels(90)      //Angle to rotate x-axis labels.
            .showControls(true)   //Allow user to switch between 'Grouped' and 'Stacked' mode.
            .groupSpacing(0.1)    //Distance between each group of bars.

    ;

    chart.xAxis
        .tickFormat(function(d){
            return d3.time.format('%d-%b')(new Date(d))//(new Date(d))
        })

    chart.yAxis
        .axisLabel(y_axis_label)
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
    //console.log('get vis'.concat(ca))
    //console.log(dat)
    if (dat == null){
        chart_ajax_error(chart_area, 'null')
    }else{

        if (ca.data('series') == 'branch' ||
                ca.data('series') == 'gender' ||
                ca.data('series') == 'rating' ||
                ca.data('series') == 'age'){

            nvd3chart(chart_area, dat['dat'], dat['y_axis'] )

        }
        else if (ca.data('series') == 'quote'){
            extract_quote(chart_area, dat)
        }
        else if(ca.data('series') == 'app_names'){
            extract_app_names(chart_area, dat)
            //ca.html("success")
        }
        else if(ca.data('series') == 'app_feedback'){
            extract_app_feedback(chart_area, dat)
        }
        else {
            chart_ajax_error(chart_area, 'series')
        }


        hidespinner(chart_area)

    }
}

function get_post_data(chart_area){
    var ca = $(chart_area);
    var filters = $(ca).siblings('.filters').children('select');
    var data = {};
    data['desired_series'] = ca.data("series");
    //data['desired_filters'] = {};

    for (ii=0; ii < filters.length; ii++){
        var this_filter = $(filters[ii]);
        if (this_filter.val() != null && this_filter.val() == ""){
            data[this_filter.data('plc')] = this_filter.val()
        }
    }

    data['intf'] = $(chart_area).data("report_num");

    return data
}


function do_chart_ajax(chart_section) {

    var ca = get_chart_area(chart_section)
    $(ca).children().hide(250)
    //var endpoint = get_endpoint(ca)
    var post_data = get_post_data(ca) //todo!

    clear_chart_ajax_error(ca)
    showspinner(ca)

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
