from django import forms
from django.db import models
from django.test import TestCase
from django.core.exceptions import ValidationError

from rest_framework import serializers as rf_serializers

from ..models import (
    DefinableSerializerByJSONField,
    DefinableSerializerByYAMLField,
    AbstractDefinitiveSerializerModel,
)

from copy import deepcopy

_correct_single_definition_data = {
    "main": {
        "name": "TestSerializer",
        "fields": [
            {
                "name": "char_field",
                "field": "CharField"
            },
            {
                "name": "integer_Field",
                "field": "IntegerField"
            },
            {
                "name": "depending_one",
                "field": "DependOneSerializer"
            }
        ]
    },
    "depending_serializers": [
        {
            "name": "DependOneSerializer",
            "fields": [
                {
                    "name": "char_field",
                    "field": "CharField"
                }
            ]
        }
    ]
}


class ExampleJSONModel(AbstractDefinitiveSerializerModel):
    foo_bar_baz = DefinableSerializerByJSONField()


class ExampleYAMLModel(AbstractDefinitiveSerializerModel):
    foo_bar_baz = DefinableSerializerByYAMLField()


class AbstractFieldTest:

    model_class = None

    def test_field(self):
        test_model = self.model_class(foo_bar_baz=_correct_single_definition_data)
        test_model.full_clean()
        serializer = test_model.get_foo_bar_baz_serializer_class()
        self.assertTrue(issubclass(serializer, rf_serializers.Serializer))

    def test_wrong_data(self):
        # not struct data
        test_model = self.model_class(foo_bar_baz="It Is Wrong data :)")
        with self.assertRaises(ValidationError):
            test_model.full_clean()

        # no main
        data = deepcopy(_correct_single_definition_data)
        data["it_is_not_main"] = data.pop("main")
        test_model = self.model_class(foo_bar_baz=data)
        with self.assertRaises(ValidationError):
            test_model.full_clean()

        # broken field
        data = deepcopy(_correct_single_definition_data)
        data["main"]["fields"][0].pop("name")
        data["main"]["fields"][1].pop("field")
        test_model = self.model_class(foo_bar_baz=data)
        with self.assertRaises(ValidationError):
            test_model.full_clean()

        # Depending serializer not found
        data = deepcopy(_correct_single_definition_data)
        data["depending_serializers"].pop(0)
        test_model = self.model_class(foo_bar_baz=data)
        with self.assertRaises(ValidationError):
            test_model.full_clean()

    def test_render_form(self):
        class TestForm(forms.ModelForm):
            class Meta:
                fields = "__all__"
                model = self.model_class

        form = TestForm()
        form.as_table()
        form.as_p()


class TestJSONField(AbstractFieldTest, TestCase):
    model_class = ExampleJSONModel


class TestYAMLField(AbstractFieldTest, TestCase):
    model_class = ExampleYAMLModel


##############################################################################
class AbstractTestModel:
    def test_get_serializer_class(self):
        test_model = self.model_class(foo_bar_baz=_correct_single_definition_data)
        test_model.full_clean()

        # get foo_bar_baz
        serializer = test_model.get_foo_bar_baz_serializer_class()
        self.assertTrue(issubclass(serializer, rf_serializers.Serializer))

    def test_get_serializer_class_but_not_in_fields(self):
        test_model = self.model_class(foo_bar_baz=_correct_single_definition_data)
        test_model.full_clean()

        # get hoge_moge_piyo
        with self.assertRaises(AttributeError):
            serializer = test_model.get_hoge_moge_piyo_serializer_class()


class TestModelForJSON(AbstractTestModel, TestCase):
    model_class = ExampleJSONModel


class TestModelForYAML(AbstractTestModel, TestCase):
    model_class = ExampleYAMLModel
