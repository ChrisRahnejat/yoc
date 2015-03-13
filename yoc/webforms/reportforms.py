__author__ = 'aakh'

import six
from django import forms

from django.core.exceptions import ValidationError

def validate_even(value):
    if value % 2 != 0:
        raise ValidationError(u'%s is not an even number' % value)

class StrictBooleanField(forms.Field):

    def validate(self, value):

        if not isinstance(value, bool) and self.required:
            raise ValidationError(self.error_messages['required'], code='required')

    def to_python(self, value):
        """Returns a Python boolean object if and only if the input value is a boolean type."""
        # Explicitly check for the string 'False', which is what a hidden field
        # will submit for False. Also check for '0', since this is what
        # RadioSelect will provide. Because bool("True") == bool('1') == True,
        # we don't need to handle that explicitly.

        if isinstance(value, six.string_types) and value.lower() in ('false', '0'):
            value = False

        elif value is None:
            value = False

        elif value is False:
            value = False

        elif isinstance(value, six.string_types) and value.lower() in ('true', '1'):
            value = True

        elif value is True:
            value = True

        else:
            raise ValidationError(u'%s is not boolean' % value)

        return value

    def _has_changed(self, initial, data):
        # Sometimes data or initial could be None or '' which should be the
        # same thing as False.
        if initial == 'False':
            # show_hidden_initial may have transformed False to 'False'
            initial = False
        return bool(initial) != bool(data)


class GrapherForm(forms.Form):
    positives = StrictBooleanField(required=False)
    negatives = StrictBooleanField(required=False)
    neutrals = StrictBooleanField(required=False)
    number = forms.IntegerField(required=False)
    csv = StrictBooleanField(required=False)