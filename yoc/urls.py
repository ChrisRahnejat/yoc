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
)
urlpatterns += patterns('',
                        (
                        r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
)