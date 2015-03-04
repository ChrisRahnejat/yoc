from django.conf.urls import patterns, include, url
from django.contrib import admin

import settings
from views import *

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'yoc.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),

    url(r'^$', serverLinks.root, name='rootpage'),
    url(r'^login/$', serverLinks.login_page, name='login_page'),
    url(r'^do_login/$', serverLinks.do_login, name='do_login'),
    url(r'^do_logout/$', serverLinks.do_logout, name='do_logout'),

    url(r'^see_question/$', clean_up.see_question, name='see_question'),
    url(r'^give_feedback/$', clean_up.give_feedback, name='give_feedback'),
    url(r'^reporting/$', clean_up.reporting, name='reporting'),
    url(r'^thanks/$', clean_up.thanks, name='thanks'),

    # NVD3 URLS
    url(r'^grapher_view/$', visuals.grapher_view, name='grapher_view'),
    url(r'^get_some_quotes/$', visuals.get_some_quotes, name='get_some_quotes'),
    url(r'^get_name_rankings/$', visuals.get_name_rankings, name='get_name_rankings'),
    url(r'^feedback_quotes_for_app/$', visuals.feedback_quotes_for_app, name='feedback_quotes_for_app'),
)
urlpatterns += patterns('',
                        (
                        r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
)