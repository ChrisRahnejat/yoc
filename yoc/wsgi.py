"""
WSGI config for testcap project.

This module contains the WSGI application used by Django's development server
and any production WSGI deployments. It should expose a module-level variable
named ``application``. Django's ``runserver`` and ``runfcgi`` commands discover
this application via the ``WSGI_APPLICATION`` setting.

Usually you will have the standard Django WSGI application here, but it also
might make sense to replace the whole Django WSGI application with a custom one
that later delegates to the Django one. For example, you could introduce WSGI
middleware here, or combine a Django application with an application of another
framework.

"""
import os
import yoc.settings
import logging
logger = logging.getLogger(__name__)
# We defer to a DJANGO_SETTINGS_MODULE already in the environment. This breaks
# if running multiple sites in the same mod_wsgi process. To fix this, use
# mod_wsgi daemon mode with each site in its own daemon process, or use
# os.environ["DJANGO_SETTINGS_MODULE"] = "testcap.settings"
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "yoc.settings")

# This application object is used by any WSGI server configured to use this
# file. This includes Django's development server, if the WSGI_APPLICATION
# setting points here.
from django.core.wsgi import get_wsgi_application


# Apply WSGI middleware here.
# from helloworld.wsgi import HelloWorldApplication
# application = HelloWorldApplication(application)


if yoc.settings.EV =='HEROKU':
    ##UNCOMMENT THIS section FOR HEROKU PUSH, COMMENT FOR LOCAL ENVIRONMENT
    logger.info('wsgi heroku')
    from dj_static import Cling
    try:
        application = Cling(get_wsgi_application())
        # logger.info('wsgi heroku application done')
        # print 'wsgi heroku application done'
    except Exception,e:
        logger.error('wsgi heroku application error, %s'%e)
        # print 'wsgi heroku application error'
        # print e.message
    # Assign QuotaGuard to your environment's http_proxy variable
else:
    # logger.info('wsgi heroku')
    # print 'wsgi'
    application = get_wsgi_application()
