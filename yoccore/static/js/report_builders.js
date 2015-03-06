/**
 * Created by aakh on 06/03/2015.
 */


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