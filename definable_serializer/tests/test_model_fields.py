from django.test import TestCase
from django.core.exceptions import ValidationError

from ..models import (
    DefinableSerializerByJSONField,
    DefinableSerializerByYAMLField,
    AbstractDefinitiveSerializerModel,
)

from copy import deepcopy

base_defn = {
    "main": {
        "name": "TestSerializer",
         "fields": [{
            "name": "test_field",
            "field": "CharField"
        }]
    }
}

validate_method_str = """

def validate_method(self, value):
    from rest_framework import serializers
    if value != "correct_data":
        raise serializers.ValidationError("Wrong data")
    return value
"""


class ExampleJSONModelWithAllowValidateMethod(AbstractDefinitiveSerializerModel):
    serializer_defn = DefinableSerializerByJSONField(
        allow_validate_method=True,
    )


class ExampleYAMLModelWithAllowValidateMethod(AbstractDefinitiveSerializerModel):
    serializer_defn = DefinableSerializerByYAMLField(
        allow_validate_method=True,
    )


class ExampleJSONModelWithDisallowValidateMethod(AbstractDefinitiveSerializerModel):
    serializer_defn = DefinableSerializerByJSONField(
        allow_validate_method=False,
    )


class ExampleYAMLModelWithDisallowValidateMethod(AbstractDefinitiveSerializerModel):
    serializer_defn = DefinableSerializerByYAMLField(
        allow_validate_method=False,
    )


class TestDefinableSerializerByJSONField(TestCase):

    allow_class = ExampleJSONModelWithAllowValidateMethod
    disallow_class = ExampleJSONModelWithDisallowValidateMethod

    def test_allow_validate_method_for_field(self):
        defn = deepcopy(base_defn)
        defn["main"]["fields"][0]["field_validate_method"] = validate_method_str

        m = self.allow_class()
        m.serializer_defn = defn
        self.assertEqual(m.full_clean(), None)


    def test_disallow_validate_method_for_field(self):
        defn = deepcopy(base_defn)
        defn["main"]["fields"][0]["field_validate_method"] = validate_method_str

        m = self.disallow_class()
        m.serializer_defn = defn

        with self.assertRaises(ValidationError):
            m.full_clean()


    def test_allow_validate_method_for_serializer(self):
        defn = deepcopy(base_defn)
        defn["main"]["serializer_validate_method"] = validate_method_str

        m = self.allow_class()
        m.serializer_defn = defn
        self.assertEqual(m.full_clean(), None)


    def test_disallow_validate_method_for_serializer(self):
        defn = deepcopy(base_defn)
        defn["main"]["serializer_validate_method"] = validate_method_str

        m = self.disallow_class()
        m.serializer_defn = defn

        with self.assertRaises(ValidationError):
            m.full_clean()


class TestDefinableSerializerByYAMLField(TestCase):

    allow_class = ExampleYAMLModelWithAllowValidateMethod
    disallow_class = ExampleYAMLModelWithDisallowValidateMethod

    def test_allow_validate_method_for_field(self):
        defn = deepcopy(base_defn)
        defn["main"]["fields"][0]["field_validate_method"] = validate_method_str

        m = self.allow_class()
        m.serializer_defn = defn
        self.assertEqual(m.full_clean(), None)


    def test_disallow_validate_method_for_field(self):
        defn = deepcopy(base_defn)
        defn["main"]["fields"][0]["field_validate_method"] = validate_method_str

        m = self.disallow_class()
        m.serializer_defn = defn

        with self.assertRaises(ValidationError):
            m.full_clean()


    def test_allow_validate_method_for_serializer(self):
        defn = deepcopy(base_defn)
        defn["main"]["serializer_validate_method"] = validate_method_str

        m = self.allow_class()
        m.serializer_defn = defn
        self.assertEqual(m.full_clean(), None)


    def test_disallow_validate_method_for_serializer(self):
        defn = deepcopy(base_defn)
        defn["main"]["serializer_validate_method"] = validate_method_str

        m = self.disallow_class()
        m.serializer_defn = defn

        with self.assertRaises(ValidationError):
            m.full_clean()
