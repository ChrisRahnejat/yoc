# from django.http import HttpResponse, Http404, HttpResponseRedirect
# from django.contrib.auth.decorators import login_required
# from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt  # , csrf_protect


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