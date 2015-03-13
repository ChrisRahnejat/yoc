__author__ = 'krhn'

import csv as csvmod
import logging

from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, get_object_or_404, redirect

import validations
from yoccore.models import *
from yoc.grapher2 import Graph
from yoc.webforms import reportforms

logger = logging.getLogger(__name__)


@csrf_exempt
def grapher_view(request):
    """
        Should handle all numerical graph types, see Graph or sub-function for
        acceptable POST fields (below)
        {
            desired_series:<str>
            desired_filters:<dict>
        }

    """

    def return_cleaned_grapher_inputs(cpost):
        """
            Acceptable keys for POST can be seen here
        """

        try:
            desired_series = cpost['desired_series']
        except KeyError:
            logger.info("No desired series specified for grapher")
            return False

        if desired_series not in ['age', 'total', 'gender', 'topic',
                                  'branch', 'rating', 'app']:
            logger.info("desired_series provided %s was no valid" %
                        desired_series)
            return False

        try:
            desired_filters = cpost['desired_filters']
        except KeyError:
            logger.info("no desired filters were provided, which is fine, "
                        "but FYI")
            desired_filters = {}

        keys_to_kill = []
        for k in desired_filters:
            if k not in ['age', 'gender', 'branch', 'topic', 'app']:
                logger.info("invalid filter %s was passed in" % k)
                keys_to_kill.append(k)

            elif k == 'age':
                supported_ages = ['>55', '46-55', '26-35', '<18', '36-45',
                                  '18-25', None]
                if any([v not in supported_ages for v in desired_filters[k]]):
                    logger.info("at least one value for age filters was not "
                                "supported")
                    keys_to_kill.append(k)

            elif k == 'gender':
                if any(
                        [v not in ['Male', 'Female',
                                   'Would rather not disclose',
                                   'Other', None] for v in desired_filters[k]]):
                    logger.info("at least one value for gender filters was "
                                "not supported")
                    keys_to_kill.append(k)

            elif k == 'branch':
                if any([v not in ['M', 'S'] for v in desired_filters[k]]):
                    logger.info("at least one value for branch filters was not "
                                "supported")
                    keys_to_kill.append(k)

            elif k == 'topic':
                if any(
                        [v not in [None] + zip(*CleanedAnswer.topics)[0] for v
                         in desired_filters[k]]):
                    logger.info(
                        "at least one value for topic filters was not supported")
                    keys_to_kill.append(k)

            elif k == 'app':
                if any([v not in ['HM', 'MM', 'SP', 'Any'] for v in
                        desired_filters[k]]):
                    logger.info("at least one value for app filters was not "
                                "supported")
                    keys_to_kill.append(k)

        if not keys_to_kill:
            logger.info("the following filters were dropped: %s" % keys_to_kill)

        for k in keys_to_kill:
            desired_filters.pop(k, None)

        return desired_series, desired_filters

    post = validations.clean_data(request)

    x = return_cleaned_grapher_inputs(post)

    if x is False:
        data = None

    else:
        desired_series, desired_filters = x
        data = Graph().get_ratings_data(desired_series, **desired_filters)

    return HttpResponse(json.dumps(data), content_type="application/json")

@csrf_exempt
def get_quotes(request):
    """
        POST:

        'csv': True if you want a CSV download, False if you want normal
        httpresponse (defaults to httpresponse if not included)

        'positive': True if you want positive quotes included (defaults to True)
        'negative': True if you want negative quotes included (defaults to True)
        'neutral': True if you want neutral quotes included (defaults to False)

        'number': number of (each type) of quote to include (defaults to ALL)

    """

    # post = validations.clean_data(request)
    if request.method != 'POST':
        template = 'yoccore/quotes.html'

        quotes = Graph().get_quotes_data(True, True, True, None)

        return render(request, template, {'quotes':quotes})

    fm = reportforms.GrapherForm(request.POST)

    if fm.is_valid():
        cd = fm.cleaned_data

        csv = cd.get('csv', False)
        positives = cd.get('positives', True)
        negatives = cd.get('negatives', True)
        neutrals = cd.get('neutrals', False)
        number = cd.get('number', None)  # None means ALL

    else:
        resp = { 'success' : False, 'errors' : [(k, v[0]) for k, v in fm.errors.items()] }
        return HttpResponseBadRequest(json.dumps(resp), content_type="application/json")



    if number and number < 1:
        number = 1

    quotes = Graph().get_quotes_data(positives, negatives, neutrals, number)

    def enhance_list(quote_list):
        output = []

        for q in quote_list:
            quote = q.answer.answer_text
            gender = q.answer.what_gender()
            age = q.answer.what_age()

            output.append({'quote': quote.lower(), 'gender': gender, 'age': age})

        return output

    if csv:
        response = HttpResponse(content_type="text/csv")
        response['Content-Disposition'] = 'attachment; filename="quotes.csv"'

        writer = csvmod.writer(response)
        writer.writerow(quotes[0].keys())

        for quote in quotes:
            writer.writerow(quote.values())

        return response

    else:
        return HttpResponse(json.dumps(quotes), content_type="application/json")