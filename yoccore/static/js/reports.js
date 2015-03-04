/**
 * Created by aakh on 04/03/2015.
 */

//$('.chart_section_toggle').on('click', function(){
//    var tgl = $(this);
//    var this_section = tgl.parent().parent();
//    tgl.addClass('maxed');
//
//    $('.chart_section').hide(250, function(){
//             this_section.make huge
//    })
//
//
//})

function get_colour_for_branch(branch){
    if (branch=='moorgate'||branch=='m'||branch=='Moorgate'||branch=='M') {
        return '#211E31'
    }
    else {
        return '#666666'
    }
}

function get