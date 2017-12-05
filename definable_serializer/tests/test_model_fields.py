from django.test import TestCase
from django.core.exceptions import ValidationError

from ..models import (
    DefinableSerializerByJSONField,
    DefinableSerializerByYAMLField,
    AbstractDefinitiveSerializerModel,
)

from copy import deepcopy

BASE_DEFN = {
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


class SpecifyBaseClassesModel(AbstractDefinitiveSerializerModel):
    class TestClass():
        IamTestClass = True

    serializer_defn = DefinableSerializerByYAMLField(
        allow_validate_method=True,
        base_classes=[TestClass]
    )


class TestSpecifyBaseClasses(TestCase):

    def test_specify_base_class(self):
        defn = deepcopy(BASE_DEFN)
        defn["main"]["fields"][0]["field_validate_method"] = validate_method_str

        m = SpecifyBaseClassesModel()
        m.serializer_defn = defn
        m.full_clean()

        serializer_class = m.get_serializer_defn_serializer_class()
        self.assertTrue(hasattr(serializer_class(), "IamTestClass"))



class TestDefinableSerializerByJSONField(TestCase):

    allow_class = ExampleJSONModelWithAllowValidateMethod
    disallow_class = ExampleJSONModelWithDisallowValidateMethod

    def test_allow_validate_method_for_field(self):
        defn = deepcopy(BASE_DEFN)
        defn["main"]["fields"][0]["field_validate_method"] = validate_method_str

        m = self.allow_class()
        m.serializer_defn = defn
        self.assertEqual(m.full_clean(), None)


    def test_disallow_validate_method_for_field(self):
        defn = deepcopy(BASE_DEFN)
        defn["main"]["fields"][0]["field_validate_method"] = validate_method_str

        m = self.disallow_class()
        m.serializer_defn = defn

        with self.assertRaises(ValidationError):
            m.full_clean()


    def test_allow_validate_method_for_serializer(self):
        defn = deepcopy(BASE_DEFN)
        defn["main"]["serializer_validate_method"] = validate_method_str

        m = self.allow_class()
        m.serializer_defn = defn
        self.assertEqual(m.full_clean(), None)


    def test_disallow_validate_method_for_serializer(self):
        defn = deepcopy(BASE_DEFN)
        defn["main"]["serializer_validate_method"] = validate_method_str

        m = self.disallow_class()
        m.serializer_defn = defn

        with self.assertRaises(ValidationError):
            m.full_clean()



class TestDefinableSerializerByYAMLField(TestCase):

    allow_class = ExampleYAMLModelWithAllowValidateMethod
    disallow_class = ExampleYAMLModelWithDisallowValidateMethod

    def test_allow_validate_method_for_field(self):
        defn = deepcopy(BASE_DEFN)
        defn["main"]["fields"][0]["field_validate_method"] = validate_method_str

        m = self.allow_class()
        m.serializer_defn = defn
        self.assertEqual(m.full_clean(), None)


    def test_disallow_validate_method_for_field(self):
        defn = deepcopy(BASE_DEFN)
        defn["main"]["fields"][0]["field_validate_method"] = validate_method_str

        m = self.disallow_class()
        m.serializer_defn = defn

        with self.assertRaises(ValidationError):
            m.full_clean()

    def test_allow_validate_method_for_serializer(self):
        defn = deepcopy(BASE_DEFN)
        defn["main"]["serializer_validate_method"] = validate_method_str

        m = self.allow_class()
        m.serializer_defn = defn
        self.assertEqual(m.full_clean(), None)


    def test_disallow_validate_method_for_serializer(self):
        defn = deepcopy(BASE_DEFN)
        defn["main"]["serializer_validate_method"] = validate_method_str

        m = self.disallow_class()
        m.serializer_defn = defn

        with self.assertRaises(ValidationError):
            m.full_clean()
