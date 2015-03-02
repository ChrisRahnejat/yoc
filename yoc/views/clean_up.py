__author__ = 'aakh'

import logging
logger = logging.getLogger(__name__)

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
import validations

@login_required
def see_question(request):

    template = 'yoc_app/questions.html'

    if 'q' in request.session['q_ctxt'].keys() and 'a' in request.session['q_ctxt'].keys():
        context = {
            'q': request.session['q_ctxt']['q'],
            'a': request.session['q_ctxt']['a'],
            'err': request.session.pop('err','Submission error'),
            'err_vals': request.session.pop('err_vals', {})
        }

    else:
        a = None
        # a = Answers.objects.all() # todo: chris to complete based on model

        q = None
        # q = a.question__text # todo: chris to complete based on model

        context = {'q': q, 'a':a}
        request.session['q_ctxt'] = context


    return render(request, template, context)

@login_required
def give_feedback(request):

    post_data = validations.clean_data(request)
    err = False

    """
    expected keys for post data are:
        quotable: BOOL,
        topic: STR,
        rating: int
    """

    try:
        # todo: chris to complete based on model
        CleanUps.create(**post_data)

    except Exception, e:
        logger.info('Clean Up object creation failed')
        err = True
        request.session['err'] = 'Something went wrong'
        request.session['err_vals'] = post_data

    if err is False:
        request.session.pop('q_ctxt')

    return redirect('see_question')
