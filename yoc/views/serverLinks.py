__author__ = 'aakh'
import logging
from django.contrib import auth
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, redirect
logger = logging.getLogger(__name__)


def root(request):
    """
    Redirects to the homepage
    """
    logger.info('redirecting from root to login')
    return redirect('login_page')


# url(r'^login/$', serverLinks.login_page, name='login_page'),
def login_page(request):
    template = 'tccore/login.html'
    context = {
        'pgtitle': 'Welcome to Test Rocket',
        'abouttitle': "Log in",
        'loginMethod': 'do_login',
        'loginPage': True,
        'hideBar': True,
        'next_page': 'see_question'
    }
    try:
        context.update({'next_page': str(request.GET['next'])})
    except:
        context.update({'next_page': 'see_question'})

    return render(request, template, context)


def common_login(request):
    """
    performs common functions between tester and non tester logins

    :param request:
    :return:
    """

    username = request.POST.get('username', '')
    password = request.POST.get('pw', '')

    logger.debug("%s, %s" % (username, password))

    user = auth.authenticate(username=username, password=password)

    if user is None:
        logger.info("user %s not permissioned" % (username))
        request.session.setdefault('up_error', True)
        return redirect('login')

    if not user.is_active:
        logger.info("user %s log in failed" % (username))
        request.session.setdefault('ua_error', True)
        return redirect('login')

    logger.info("user %s authenticated in" % user.id)

    auth.login(request, user)

# url(r'^do_login/$', serverLinks.do_login, name='do_login'),
def do_login(request):
    logger.debug('request.POST.iteritems(): %s' % [(k, v) for k, v in request.POST.iteritems()])

    common_login(request)
    request.session['user_initials'] = request.user.username
    request.session['ctr'] = 0

    next_page = request.POST.get('next_page', 'see_question')

    return redirect(next_page)

# url(r'^do_logout/$', serverLinks.do_logout, name='do_logout'),
#  Logout (removes living-id from cache, clears cookies / session)
def do_logout(request):
    auth.logout(request)
    logger.info("user %s logged out" % request.user.id)
    return redirect('tester_rootpage')

