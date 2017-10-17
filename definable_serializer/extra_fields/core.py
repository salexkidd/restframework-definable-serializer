from rest_framework import serializers as rf_serializers
from rest_framework import fields as rf_fields


class CheckRequiredField(rf_fields.BooleanField):
    """
    CheckRequiredField

    definable_serializer.extra_fields.CheckRequiredField
    """
    custom_error_messages = {
        'please_be_sure_to_turn_it_on': 'Please be sure to turn it on.'
    }

    def to_internal_value(self, data):
        data = super().to_internal_value(data)
        if data == "" or data is None or data is False:
            self.fail('please_be_sure_to_turn_it_on')
        return data

    def __init__(self, *args, **kwargs):
        kwargs["style"] = {'base_template': 'checkbox.html',}
        super().__init__(*args, **kwargs)
        self.error_messages.update(self.custom_error_messages)


class MultipleCheckboxField(rf_fields.MultipleChoiceField):
    """
    MultipleCheckboxField

    definable_serializer.extra_fields.MultipleCheckboxField
    """

    custom_error_messages = {
        'this_field_is_required': 'This field is required.'
    }

    def __init__(self, *args, **kwargs):
        self.requred = kwargs.pop("required", False)
        kwargs["style"] = {
            'base_template': 'checkbox_multiple.html',
            'inline': kwargs.pop('inline', False)
        }

        super().__init__(*args, **kwargs)
        self.error_messages.update(self.custom_error_messages)

    def to_internal_value(self, data):
        data = super().to_internal_value(data)
        if self.requred and not len(data):
            self.fail('this_field_is_required')

        return data


class NonNullableChoiceField(rf_fields.ChoiceField):
    """
    ChoiceWithDashedField

    definable_serializer.extra_fields.NonNullableChoiceField
    """
    custom_error_messages = {
        'this_field_is_required': 'This field is required.'
    }

    def __init__(self, choices, *args, **kwargs):
        super().__init__(choices, *args, **kwargs)
        self.error_messages.update(self.custom_error_messages)

    def to_internal_value(self, data):
        data = super().to_internal_value(data)
        if data == "" or data is None:
            self.fail('this_field_is_required')
        return data


class RadioField(rf_fields.ChoiceField):
    """
    RadioField

    definable_serializer.extra_fields.RadioField
    """
    def __init__(self, *args, **kwargs):
        kwargs["style"] = {
            'base_template': 'radio.html',
            'inline': kwargs.pop('inline', False)
        }

        super().__init__(*args, **kwargs)


class TextField(rf_fields.CharField):
    """
    TextField

    definable_serializer.extra_fields.TextField
    """
    def __init__(self, *args, **kwargs):
        kwargs["style"] = {
            'base_template': 'textarea.html',
            'rows': kwargs.pop('rows', 5),
            'placeholder': kwargs.pop('placeholder', "")
        }

        super().__init__(*args, **kwargs)
