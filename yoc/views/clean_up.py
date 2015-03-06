__author__ = 'aakh'

import logging, json
logger = logging.getLogger(__name__)

from yoccore import models
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt  # , csrf_protect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django import forms
import validations, visuals

class CleanUpform(forms.ModelForm):
    class Meta:
        model = models.CleanedAnswer

class IntForm(forms.Form):
    intf = forms.IntegerField(min_value=1, max_value=7)


@csrf_exempt
@user_passes_test(lambda u: u.is_staff)
def get_report_url(request):

    form = IntForm(request.POST)

    if form.is_valid():
        urls = ("/grapher_view/","/grapher_view2/",#todo!!

                "/get_some_quotes/","/grapher_view/",
         "/grapher_view/","/get_name_rankings","/feedback_quotes_for_app/")

        data = urls[form.cleaned_data['intf']-1]

    else:
        data = False

    return HttpResponse(json.dumps(data), content_type="application/json")


@csrf_exempt
@user_passes_test(lambda u: u.is_staff)
def reporting(request):

    if request.method=="POST":
        urls = (visuals.grapher_view,
                visuals.grapher_view,#todo:2
                visuals.get_some_quotes,
                visuals.grapher_view,
                visuals.grapher_view,
                visuals.get_name_rankings,
                visuals.feedback_quotes_for_app,)

        outcomes = (
            'count',
            'sum',
            '',
            'average',
            'average',
            '',
            '',
        )

        intf = int(request.POST['intf'])-1
        return urls[intf](request, outcomes[intf])


    template = 'yoccore/reporting.html'

    supported_ages = ['>55','46-55','26-35','<18','36-45','18-25']
    supported_genders = ['Male', 'Female', 'Would rather not disclose', 'Other']
    age_filter = ('age',supported_ages)
    gender_filter = ('gender',supported_genders)
    branch_filter = ('branch',['Moorgate','Shoreditch'])
    titles = (
            'We have had %s conversations in the last 2 weeks'%models.Session.objects.all().count(),
            '%s %% of feedback was positive'%100,
            'Some quotes from customers',
            'Feedback score by gender',
            'Feedback score by age',
            'Suggested names for apps',
            'Feedback on the apps',
        )


    ctxt = {'chart_config':[
        {'series': 'branch','report_num':1, 'filters':[gender_filter, age_filter]},
        {'series': 'rating','report_num':2, 'filters':[branch_filter, gender_filter, age_filter]},
        {'series':'quote', 'report_num':3, 'filters':[branch_filter, gender_filter, age_filter]},
        {'series': 'gender','report_num':4, 'filters':[branch_filter, age_filter]},
        {'series': 'age','report_num':5, 'filters':[branch_filter, gender_filter]},
        {'series': 'app_names','report_num':6, 'filters':[branch_filter, gender_filter, age_filter]},
        {'series': 'app_feedback','report_num':7, 'filters':[branch_filter, gender_filter, age_filter]},
        ],
            'titles':titles,
            }

    return render(request, template, ctxt)

@csrf_exempt
@login_required
def thanks(request):

    template = 'yoccore/thanks.html'
    return render(request, template, {})

@login_required
def see_question(request):

    template = 'yoccore/questions.html'

    choices = (
        'not applicable',
        'negative',
        'somewhat negative',
        'neutral',
        'somewhat postitive',
        'postitive',
    )


    if request.session['q_ctxt'].get('q',None) is not None and request.session['q_ctxt'].get('a',None) is not None:

        context = {
            'q': request.session['q_ctxt']['q'],
            'a': request.session['q_ctxt']['a'],
            'a_id': request.session['q_ctxt']['a_id'],
            'err': request.session.pop('err','Submission error'),
            'err_vals': request.session.pop('err_vals', {}),
            'choices': choices,
            'topics': models.CleanedAnswer.topics,
            'pgtitle': 'help make sense of this'
        }

    else:
        user_initials = request.session['user_initials']  # todo: this needs to work
        
        # all answer object for this person which need cleaning up
        Q1 = Q(session__user_initials__iexact=user_initials.strip())
        Q2 = Q(done=False)
        answers = models.Answer.objects.filter(Q1 & Q2)

        if len(answers) < 1:
            a, q, a_id = None, None, None

            return redirect('thanks')

        else:
            ans = answers[0]
            q = ans.question.question_text
            a = ans.answer_text
            a_id = ans.id

        context = {'q': q, 'a': a, 'a_id': a_id, 'choices': choices,
            'topics': models.CleanedAnswer.topics, 'pgtitle': 'help make sense of this'
        }
        request.session['q_ctxt'] = context
        request.session['q_left'] = len(answers)


    return render(request, template, context)

@login_required
def give_feedback(request):

    post_data = validations.clean_data(request)
    form = CleanUpform(request.POST)
    err = False

    """
    expected keys for post data are:
        quotable: BOOL,
        topic: STR, (from models.CleanedAnswer.topics)
        rating: int, (1 to 5)
        answer_id: int,
        not_feedback: BOOL (defaults to False ,so optional, but pass True if not feedback)
    """

    if form.is_valid():
        dat = form.cleaned_data
        models.CleanedAnswer.create(**dat)

    # try:
    #     # todo: chris to complete based on model
    #     models.CleanedAnswer.create(**post_data)
    #
    # except Exception, e:
    #     logger.info('Clean Up object creation failed')
    #     logger.info('%s'%e.message)
    else:
        err = True
        request.session['err'] = 'Something went wrong'
        request.session['err_vals'] = post_data

    if err is False:
        request.session['q_ctxt'] = {}
        request.session['ctr'] += 1

    return redirect('see_question')


