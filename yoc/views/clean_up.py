__author__ = 'aakh'

from django.shortcuts import render, get_object_or_404, redirect
import validations

def see_question(request):

    template = 'yoc_app/questions.html'

    if 'q' in request.session['q_ctxt'].keys() and 'a' in request.session['q_ctxt'].keys():
        context = {
            'q': request.session['q_ctxt']['q'],
            'a': request.session['q_ctxt']['a'],
            'err': request.session.get('err','Submission error')

        }

    else:
        a = None
        # a = Answers.objects.all() # todo: chris to complete based on model

        q = None
        # q = a.question__text # todo: chris to complete based on model

        context = {'q': q, 'a':a}


    return render(request, template, context)

def give_feedback(request):

    post_data = validations.clean_data(request)


    return redirect('see_question')
