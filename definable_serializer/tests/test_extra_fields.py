from django.test import TestCase
from rest_framework import serializers as rf_serializers

from .. import extra_fields


class CheckRequiredFieldSerializer(rf_serializers.Serializer):
    target_field = extra_fields.CheckRequiredField()


class TestCheckRequiredField(TestCase):
    def test_required_check_if_true(self):
        serializer = CheckRequiredFieldSerializer(data={"target_field": True})
        self.assertTrue(serializer.is_valid())

    def test_required_check_if_false(self):
        serializer = CheckRequiredFieldSerializer(data={"target_field": False})
        self.assertFalse(serializer.is_valid())

    def test_required_check_if_none_and_null(self):
        serializer = CheckRequiredFieldSerializer(data={"target_field": None})
        self.assertFalse(serializer.is_valid())

        serializer = CheckRequiredFieldSerializer(data={})
        self.assertFalse(serializer.is_valid())


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
class MultipleCheckboxFieldAndRequiredSerializer(rf_serializers.Serializer):
    target_field = extra_fields.MultipleCheckboxField(
        ((1, "one"), (2, "two"), (3, "three"),),
        required=True,
    )


class TestMultipleCheckboxFieldAndRequired(TestCase):
    def test_multiple_checkbox_field(self):
        serializer = MultipleCheckboxFieldAndRequiredSerializer(
            data={"target_field": [1, 2, 3]}
        )
        self.assertTrue(serializer.is_valid())

    def test_required(self):
        serializer = MultipleCheckboxFieldAndRequiredSerializer(
            data={"target_field": []}
        )
        self.assertFalse(serializer.is_valid())

#      -      -      -      -      -      -      -      -      -      -      -

class MultipleCheckboxFieldAndNotRequiredSerializer(rf_serializers.Serializer):
    target_field = extra_fields.MultipleCheckboxField(
        ((1, "one"), (2, "two"), (3, "three"),),
        required=False,
    )


class TestMultipleCheckboxFieldAndNotRequired(TestCase):
    def test_multiple_checkbox_field(self):
        serializer = MultipleCheckboxFieldAndNotRequiredSerializer(
            data={"target_field": [1, 2, 3]}
        )
        self.assertTrue(serializer.is_valid())

    def test_required(self):
        serializer = MultipleCheckboxFieldAndNotRequiredSerializer(
            data={"target_field": []}
        )
        self.assertTrue(serializer.is_valid())


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
class ChoiceWithBlankFieldSerializer(rf_serializers.Serializer):
    target_field = extra_fields.ChoiceWithBlankField(
        (
            (1, "one"),
            (2, "two"),
            (3, "three"),
        ),
    )


class TestChoiceWithBlankField(TestCase):
    def test_choice_null_value(self):
        serializer = ChoiceWithBlankFieldSerializer(
            data={"target_field": ""}
        )
        self.assertFalse(serializer.is_valid())

    def test_choice_valid_value(self):
        serializer = ChoiceWithBlankFieldSerializer(
            data={"target_field": "1"}
        )
        self.assertTrue(serializer.is_valid())

    def test_choice_invalid_value(self):
        serializer = ChoiceWithBlankFieldSerializer(
            data={"target_field": "-1"}
        )
        self.assertFalse(serializer.is_valid())


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
class RadioFieldSerializer(rf_serializers.Serializer):
    target_field = extra_fields.RadioField(
        (
            (1, "one"),
            (2, "two"),
            (3, "three"),
        ),
    )


class TestRadioField(TestCase):
    def test_choice_null_value(self):
        serializer = RadioFieldSerializer(
            data={"target_field": ""}
        )
        self.assertFalse(serializer.is_valid())


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
class TextFieldSerializer(rf_serializers.Serializer):
    target_field = extra_fields.TextField(
        rows=10,
        placeholder="Hello!"
    )


class TestTextField(TestCase):
    def test_textfield(self):
        serializer = TextFieldSerializer(data={"target_field": "Hello!"})
        self.assertTrue(serializer.is_valid())
