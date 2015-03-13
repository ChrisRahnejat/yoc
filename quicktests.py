import os
import json
from django.test import Client

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "yoc.settings")

def test_get_quotes2():
    c = Client()
    response = c.post('/get_quotes2/', {'positive': False, 'negative': False})
    response2 = c.post('/get_quotes2/', {'csv': True})

    print json.dumps(json.loads(response.content), indent=2)
    print json.dumps(json.loads(response2.content), indent=2)


def test_post(url, post_data ):
    c = Client()
    response = c.post('/'.join([url]), post_data)

    return response


def test_get(url, get_data):
    c = Client()
    response = c.post('/'.join([url]), get_data)

    return response

def pretty_print(dat):
    return json.dumps(json.loads(dat), indent=2)