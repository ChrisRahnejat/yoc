# from django.http import HttpResponse, Http404, HttpResponseRedirect
# from django.contrib.auth.decorators import login_required
# from django.core.urlresolvers import reverse
# from dateutil.relativedelta import relativedelta
# from datetime import datetime
import logging
logger = logging.getLogger(__name__)
from django.views.decorators.csrf import csrf_exempt  # , csrf_protect


class Numbers():
    @staticmethod
    def int_or_none(val):
        try:
            return int(val)
        except Exception,e:
            logger.info(e.message)
            return None

    @staticmethod
    def sum_list(list_to_sum, *args):
        cleaned_list_to_sum = [x for x in list_to_sum if x is not None]
        try:
            return round(float(reduce(lambda x, y: x + y, cleaned_list_to_sum)),2)
        except Exception,e:
            logger.info(e.message)
            return 0
    @staticmethod
    def average_list(list_to_average, *args):
        cleaned_list_to_average = [x for x in list_to_average if x is not None]
        try:
            return Numbers.sum_list(list_to_average) / len(cleaned_list_to_average)

        except Exception,e:
            logger.info(e.message)
            return 0


class DataValidations():
    @staticmethod
    def is_empty(query_item):
        return query_item in [(), {}, [], None, '', ' ', ]


@csrf_exempt
def clean_data(request):
    if request.method == 'POST':
        post_values = dict(request.POST)  # use this as iterable items for a key are not lost
    elif request.method == 'GET':
        post_values = dict(request.GET)
    else:
        return request

    for x in post_values.items():
        if isinstance(x[1], (list, tuple)):
            if all([DataValidations.is_empty(y) for y in x[1]]):
                post_values.pop(x[0])
            elif len(x[1]) == 1:
                post_values[x[0]] = x[1][0]

        if DataValidations.is_empty(x[1]) or x[0] == u'csrfmiddlewaretoken':
            post_values.pop(x[0])

    return post_values