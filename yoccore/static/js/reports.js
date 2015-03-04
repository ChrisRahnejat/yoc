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

function get_endpoint(report_num){
    if (report_num == 1||report_num == 2||report_num == 4||report_num == 5 ){
        return "/grapher_view/"
    }
    else if (report_num == 3) {
        return "/get_some_quotes/"
    }
    else if (report_num == 6) {
        return "/get_name_rankings/"
    }
    else if (report_num == 7) {
        return "/feedback_quotes_for_app/"
    }
    else {
        return 0
    }
}

function split_sptring_by_comma(str){
    return false
}

function build_post_params(ele){
    return false
}

// ajax
//$.ajax({
//        type: "POST",
//        url: "/testers/answers/",
//        data: answers,
//
//        success: function () {
//
//
//            curr_section.hide(350);
//            questionnaire_success(goto_next_qs, next_section, curr_section);
//
//        },
//        error: function(jqXHR, exception){
//            $("#question_submit").html("Not sure that saved. Please try again?");
//            console.log(exception)
//        },
//        complete: function() {
//            submitRunning = false;
//
//        }
//    }).done(function() {
//        curr_section.addClass( "done" );
//
//        })