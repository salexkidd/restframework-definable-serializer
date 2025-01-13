from django.db.models.fields import BLANK_CHOICE_DASH

try:
    from django.utils.translation import ugettext_lazy as _
except ImportError:
    from django.utils.translation import gettext_lazy as _

from rest_framework import serializers as rf_serializers
from rest_framework import fields as rf_fields
from copy import copy
import warnings


class CheckRequiredField(rf_fields.BooleanField):
    """
    CheckRequiredField

    definable_serializer.extra_fields.CheckRequiredField
    """
    def to_internal_value(self, data):
        data = super().to_internal_value(data)
        if data == "" or data is None or data is False:
            self.fail('required')
        return data

    def __init__(self, *args, **kwargs):
        kwargs["style"] = {'base_template': 'checkbox.html',}
        super().__init__(*args, **kwargs)


class MultipleCheckboxField(rf_fields.MultipleChoiceField):
    """
    MultipleCheckboxField

    definable_serializer.extra_fields.MultipleCheckboxField
    """
    def __init__(self, choices, required=False, inline=False, **kwargs):
        self.requred = required
        kwargs["style"] = {
            'base_template': 'checkbox_multiple.html',
            'inline': inline,
            'source': "test",
        }
        kwargs["choices"] = choices
        super().__init__(**kwargs)

    def to_internal_value(self, data):
        data = super().to_internal_value(data)
        if self.requred and not len(data):
            self.fail('required')
        return data


class ChoiceWithBlankField(rf_fields.ChoiceField):
    """
    ChoiceWithBlankField

    definable_serializer.extra_fields.ChoiceWithBlankField
    """
    def __init__(self, choices, *args, blank_label=None, **kwargs):
        warnings.warn(
            "ChoiceWithBlankField' will be deprecated in the future. "
            "Please use to 'RequireChoiceField'.",
            PendingDeprecationWarning
        )
        blank_choices = copy(BLANK_CHOICE_DASH)
        blank_label = blank_label or blank_choices[0][1]
        if blank_label:
            blank_choices = [["", blank_label],]

        choices = tuple(blank_choices + list(choices))

        super().__init__(choices, *args, **kwargs)

    def to_internal_value(self, data):
        data = super().to_internal_value(data)
        if data == "" or data is None:
            self.fail('required')
        return data


class ChoiceRequiredField(rf_fields.ChoiceField):
    """
    ChoiceRequiredField

    definable_serializer.extra_fields.ChoiceRequiredField
    """
    def __init__(self, choices, *args, **kwarsg):
        super().__init__(choices, *args, **kwarsg)
        first_value = choices[0][0]

        if first_value is not None:
            raise ValueError(
                "first choice value must be blank or None. "
                "({}, {})".format(choices[0][0], choices[0][1]))

    def to_internal_value(self, data):
        data = super().to_internal_value(data)
        if data == "" or data is None or data is False:
            self.fail('required')
        return data


class RadioField(rf_fields.ChoiceField):
    """
    RadioField

    definable_serializer.extra_fields.RadioField
    """
    def __init__(self, *args, inline=False, **kwargs):
        kwargs["style"] = {
            'base_template': 'radio.html',
            'inline': inline,
        }
        super().__init__(*args, **kwargs)


class TextField(rf_fields.CharField):
    """
    TextField

    definable_serializer.extra_fields.TextField
    """
    def __init__(self, *args, rows=5, placeholder="", **kwargs):
        warnings.warn(
            "TextField will be deprecated in the future.",
            PendingDeprecationWarning
        )
        style = kwargs.get("style", dict())
        style.update({
            'base_template': 'textarea.html',
            'rows': rows,
            'placeholder': kwargs.get("style", {}).get("placeholder", placeholder)
        })
        kwargs["style"] = style
        super().__init__(*args, **kwargs)
