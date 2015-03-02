__author__ = 'aakh'

import logging
logger = logging.getLogger(__name__)

from yoccore import models

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q

import validations

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

        else:
            ans = answers[0]
            q = ans.question.question_text
            a = ans.answer_text
            a_id = ans.id

        context = {'q': q, 'a': a, 'a_id': a_id, 'choices': choices,
            'topics': models.CleanedAnswer.topics, 'pgtitle': 'help make sense of this'
        }
        request.session['q_ctxt'] = context


    return render(request, template, context)

@login_required
def give_feedback(request):

    post_data = validations.clean_data(request)
    err = False

    """
    expected keys for post data are:
        quotable: BOOL,
        topic: STR, (from models.CleanedAnswer.topics)
        rating: int, (1 to 5)
        answer_id: int,
        not_feedback: BOOL (defaults to False ,so optional, but pass True if not feedback)
    """

    try:
        # todo: chris to complete based on model
        models.CleanedAnswer.create(**post_data)

    except Exception, e:
        logger.info('Clean Up object creation failed')
        err = True
        request.session['err'] = 'Something went wrong'
        request.session['err_vals'] = post_data

    if err is False:
        request.session['q_ctxt'] = {}
        request.session['ctr'] += 1

    return redirect('see_question')
