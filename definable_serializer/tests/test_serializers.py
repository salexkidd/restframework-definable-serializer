from django.test import TestCase
from django.http import HttpRequest
from django.core.exceptions import ValidationError
from rest_framework.serializers import CharField

from .. import serializers as definable_serializer

import os
import yaml
from copy import deepcopy
from collections import OrderedDict

TEST_DATA_FILE_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "data"
)


class CorrectDataValidator:
    def __init__(self, correct_data):
        self.correct_data = correct_data

    def __call__(self, value):
        if value != self.correct_data:
            raise ValidationError("Value is not '{}'".format(
                self.correct_data))


class TestSerializer(TestCase):

    def test_buildserializer(self):
        base_defn = {
            "main": {"name": "TestSerializer",
                     "fields": [{
                        "name": "test_field",
                        "field": "CharField"}]}
        }

        serializer_kls = definable_serializer.build_serializer(base_defn)
        serializer = serializer_kls()

        self.assertEqual(serializer.__class__.__name__, "TestSerializer")
        self.assertTrue(issubclass(CharField, serializer.fields["test_field"].__class__))

    def test_build_serializer_by_json(self):
        json_data = """
        {
            "main": {
                "name": "TestSerializer",
                "fields": [
                    {
                        "name": "test_field",
                        "field": "CharField"
                    }
               ]
            }

        }
        """
        serializer_kls = definable_serializer.build_serializer_by_json(json_data)
        serializer = serializer_kls()

        self.assertEqual(serializer.__class__.__name__, "TestSerializer")
        self.assertTrue(issubclass(CharField, serializer.fields["test_field"].__class__))

    def test_build_serializer_by_json_file(self):
        serializer_kls = definable_serializer.build_serializer_by_json_file(
            os.path.join(TEST_DATA_FILE_DIR, "test_build_serializer_by_json_file.json"))
        serializer = serializer_kls()

        self.assertEqual(serializer.__class__.__name__, "TestSerializer")
        self.assertTrue(issubclass(CharField, serializer.fields["test_field"].__class__))

    def test_build_serializer_by_yaml(self):
        yaml_data = """
        main:
          name: TestSerializer
          fields:
            - name: test_field
              field: CharField
        """
        serializer_kls = definable_serializer.build_serializer_by_yaml(yaml_data)
        serializer = serializer_kls()

        self.assertEqual(serializer.__class__.__name__, "TestSerializer")
        self.assertTrue(issubclass(CharField, serializer.fields["test_field"].__class__))

    def test_build_serializer_by_yaml_file(self):
        serializer_kls = definable_serializer.build_serializer_by_yaml_file(
            os.path.join(TEST_DATA_FILE_DIR, "test_build_serializer_by_yaml_file.yml"))
        serializer = serializer_kls()

        self.assertEqual(serializer.__class__.__name__, "TestSerializer")
        self.assertTrue(issubclass(CharField, serializer.fields["test_field"].__class__))

    def test_not_availabe_fields(self):
        """
        Not available below fields.
        - ListField
        - DictField
        - SerializerMethodField
        """
        base_defn = {
            "main": {
                "name": "TestSerializer",
                "fields": [{"name": "%(name)s", "field": "%(field)s"}]
            }
        }

        name_and_field_list = [
            ("list_field", "ListField",),
            ("dict_field", "DictField",),
            ("serializer_method_field", "SerializerMethodField",),
        ]

        for name, field in name_and_field_list:
            defn = deepcopy(base_defn)
            defn["main"]["fields"][0]["name"] = name
            defn["main"]["fields"][0]["field"] = field

            with self.assertRaises(ValidationError):
                definable_serializer.build_serializer(defn)

    def test_all_type_restframework_fields(self):
        defined_serializer_kls = definable_serializer.build_serializer_by_json_file(
            os.path.join(TEST_DATA_FILE_DIR, "test_all_type_fields.json"))

    def test_need_depending(self):
        defined_serializer_kls = definable_serializer.build_serializer_by_json_file(
            os.path.join(TEST_DATA_FILE_DIR, "test_need_depending.json")
        )

        # Non bound serializer
        unbound_serializer = defined_serializer_kls()

        bound_data = {
            "group_name": "Test User Group",
            "person_list": [
                {
                    "username_field": "User 0",
                    "email_field": "test-0@example.com"
                },
                {
                    "username_field": "User 1",
                    "email_field": "test-1@example.com"
                }
            ]
        }
        bound_serializer = defined_serializer_kls(data=bound_data)
        self.assertTrue(bound_serializer.is_valid())

        self.assertEqual(
            bound_serializer.data["group_name"],
            "Test User Group"
        )

        for i, user_data in enumerate(bound_serializer.data["person_list"]):
            username = "User {}".format(i)
            email = "test-{}@example.com".format(i)
            self.assertEqual(user_data["username_field"], username)
            self.assertEqual(user_data["email_field"], email)


    def test_need_depending_and_not_enoght_data(self):
        defined_serializer_kls = definable_serializer.build_serializer_by_json_file(
            os.path.join(TEST_DATA_FILE_DIR, "test_need_depending.json")
        )

        # Non bound serializer
        unbound_serializer = defined_serializer_kls()

        bound_data = {
            "group_name": "Test User Group",
            "person_list": [
                {
                    "email_field": "test-0@example.com"
                },
                {
                    "username_field": "User 1",
                }
            ]
        }
        bound_serializer = defined_serializer_kls(data=bound_data)

        self.assertFalse(bound_serializer.is_valid())

        self.assertIn(
            "username_field",
            bound_serializer.errors["person_list"][0]
        )

        self.assertIn(
            "email_field",
            bound_serializer.errors["person_list"][1]
        )


    def test_field_by_package_module_class_string(self):
        base_defn = {
            "main": {
                "name": "TestSerializer",
                "fields": [
                    {
                        "name": "package_module_class_field",
                        "field": "rest_framework.serializers.CharField"
                    }
                ]
            }
        }
        defined_serializer_kls = definable_serializer.build_serializer(base_defn)
        serializer = defined_serializer_kls()
        self.assertTrue(
            issubclass(
                CharField,
                serializer.fields["package_module_class_field"].__class__
            )
        )

    def test_serializer_not_specify_required_field(self):
        base_defn = {
            "main": {
                # "name": "TestSerializer", <- No Name!
                "fields": [
                    {
                        "name": "test_field",
                        "field": "No Field.. Sorry! :P"
                    }
                ]
            }
        }
        with self.assertRaises(ValidationError):
            defined_serializer_kls = definable_serializer.build_serializer(base_defn)

    def test_serializer_not_specify_main(self):
        base_defn = {}
        with self.assertRaises(ValidationError):
            defined_serializer_kls = definable_serializer.build_serializer(base_defn)

    def test_given_wrong_args_to_field(self):
        base_defn = {
            "main": {
                "name": "TestSerializer",
                "fields": [
                    {
                        "name": "test_field",
                        "field": "CharField",
                        "field_args": [
                            ["lotus", 1, 2, 3]
                        ]
                    }
                ]
            }
        }
        with self.assertRaises(ValidationError) as e:
            defined_serializer_kls = definable_serializer.build_serializer(base_defn)

    def test_field_specify_required_field(self):
        base_defn = {
            "main": {
                "name": "TestSerializer",
                "fields": [
                    {
                        # "name": "test_field", <- No !?
                        "field": "CharField",
                    }
                ]
            }
        }
        with self.assertRaises(ValidationError) as e:
            defined_serializer_kls = definable_serializer.build_serializer(base_defn)

    def test_specify_non_exist_field_class(self):
        base_defn = {
            "main": {
                "name": "TestSerializer",
                "fields": [
                    {
                        "name": "test_field",
                        "field": "No Field.. Sorry! :P"
                    }
                ]
            }
        }
        with self.assertRaises(ValidationError):
            defined_serializer_kls = definable_serializer.build_serializer(base_defn)

    def test_field_and_serializer_validate_method(self):
        serializer_kls = definable_serializer.build_serializer_by_yaml_file(
            os.path.join(TEST_DATA_FILE_DIR, "test_field_and_serializer_validate_method.yml"))

        # Incorrect data
        serializer = serializer_kls(data={
            "test_field_one": "incorrect_data",
            "test_field_two": "Hi",
        })
        self.assertFalse(serializer.is_valid())

        # Correct data. But test_field_two is not same field_one
        serializer = serializer_kls(data={
            "test_field_one": "correct_data",
            "test_field_two": "Hi",
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn("test_field_two", serializer.errors)

        # All Correct.
        serializer = serializer_kls(data={
            "test_field_one": "correct_data",
            "test_field_two": "correct_data",
        })
        self.assertTrue(serializer.is_valid())

    def test_field_and_serializer_validate_but_has_prolem_string(self):
        correct_serializer_define_data = None
        with open(os.path.join(TEST_DATA_FILE_DIR, "test_field_and_serializer_validate_method.yml"), "r") as fh:
            correct_serializer_define_data = yaml.load(fh)

        # For Field
        wrong_field_validate_method = deepcopy(correct_serializer_define_data)
        wrong_field_validate_method["main"]["fields"][0]["field_validate_method"] = 'validate_method = "foobar"'
        with self.assertRaises(ValidationError) as e:
            definable_serializer.build_serializer(wrong_field_validate_method)

        wrong_field_validate_method = deepcopy(correct_serializer_define_data)
        wrong_field_validate_method["main"]["fields"][0]["field_validate_method"] = "It's not a func!!"
        with self.assertRaises(ValidationError) as e:
            definable_serializer.build_serializer(wrong_field_validate_method)

        # For Serializer
        wrong_serializer_validate_method = deepcopy(correct_serializer_define_data)
        wrong_serializer_validate_method["main"]["serializer_validate_method"] = 'validate_method = "foobar"'
        with self.assertRaises(ValidationError):
            serializer_kls = definable_serializer.build_serializer(wrong_serializer_validate_method)

        wrong_serializer_validate_method = deepcopy(correct_serializer_define_data)
        wrong_serializer_validate_method["main"]["serializer_validate_method"] = "It's not a func"
        with self.assertRaises(ValidationError):
            serializer_kls = definable_serializer.build_serializer(wrong_serializer_validate_method)

    def test_using_validators(self):
        yaml_file = os.path.join(TEST_DATA_FILE_DIR, "using_validator.yml")
        serializer_class = definable_serializer.build_serializer_by_yaml_file(yaml_file)

        serializer = serializer_class(data={"using_validator_field": "correct_data"})
        self.assertTrue(serializer.is_valid())

        serializer = serializer_class(data={"using_validator_field": "wrong_data"})
        self.assertFalse(serializer.is_valid())

        self.assertEqual(
            len(serializer.fields["using_validator_field"].validators), 2
        )

    def test_using_not_exist_validators(self):

        with open(os.path.join(TEST_DATA_FILE_DIR, "using_validator.yml")) as fh:
            yaml_data = yaml.load(fh)

        yaml_data["main"]["fields"][0]["validators"][0]["validator"]  = "foo.bar.NotExistValidator"

        with self.assertRaises(ValidationError):
            serializer_class = definable_serializer.build_serializer(yaml_data)

    def test_using_not_correct_validator_args(self):
        with open(os.path.join(TEST_DATA_FILE_DIR, "using_validator.yml")) as fh:
            yaml_data = yaml.load(fh)

        yaml_data["main"]["fields"][0]["validators"][0]["kwargs"] = {"kwargs": "not_allowed"}

        with self.assertRaises(ValidationError):
            serializer_class = definable_serializer.build_serializer(yaml_data)

    def test_translation(self):

        def _check(serializer, field_name, target, correct_str):
            self.assertEqual(
                getattr(serializer.fields[field_name], target), correct_str)

        yaml_file = os.path.join(TEST_DATA_FILE_DIR, "test_translation.yml")
        serializer_class = definable_serializer.build_serializer_by_yaml_file(yaml_file)

        request = HttpRequest()
        setattr(request, "LANGUAGE_CODE", "en")
        serializer_default = serializer_class(context={"request": request})

        # label and help_text for default
        for target in ("label", "help_text",):
            for field_name in serializer_default.fields.keys():
                correct_str = "{}_{}_default".format(field_name, target)
                _check(serializer_default, field_name, target, correct_str)

        # gendar_field check
        for value, label in serializer_default.fields["gendar_field"].choices.items():
            self.assertTrue(label.endswith, "_default")

        setattr(request, "LANGUAGE_CODE", "ja")
        serializer_ja = serializer_class(context={"request": request})

        # label and help_text for default
        for target in ("label", "help_text",):
            for field_name in serializer_default.fields.keys():
                correct_str = "{}_{}_ja".format(field_name, target)
                _check(serializer_ja, field_name, target, correct_str)

        # gendar_field check
        for value, label in serializer_default.fields["gendar_field"].choices.items():
            self.assertTrue(label.endswith, "_ja")

        # not in default test
        with open(yaml_file, "r") as fh:
            yaml_data = yaml.load(fh)

        # 'default' not in label test
        copied_yaml_data = deepcopy(yaml_data)
        with self.assertRaises(ValidationError) as e:
            del(copied_yaml_data["main"]["fields"][1]["field_kwargs"]["label"]["default"])
            definable_serializer.build_serializer(copied_yaml_data)

        self.assertIn("gendar_field", e.exception.error_dict)
        self.assertEqual(
            e.exception.message_dict["gendar_field"][0],
            "'default' is required in 'label'"
        )

        # 'default' not in help_text test
        copied_yaml_data = deepcopy(yaml_data)
        with self.assertRaises(ValidationError) as e:
            del(copied_yaml_data["main"]["fields"][1]["field_kwargs"]["help_text"]["default"])
            definable_serializer.build_serializer(copied_yaml_data)

        self.assertIn("gendar_field", e.exception.error_dict)
        self.assertEqual(
            e.exception.message_dict["gendar_field"][0],
            "'default' is required in 'help_text'"
        )

        # 'default' not in choices test
        copied_yaml_data = deepcopy(yaml_data)
        with self.assertRaises(ValidationError) as e:
            del(copied_yaml_data["main"]["fields"][1]["field_args"][0][0][1]["default"])
            definable_serializer.build_serializer(copied_yaml_data)

        self.assertIn("gendar_field", e.exception.error_dict)
        self.assertEqual(
            e.exception.message_dict["gendar_field"][0],
            "'default' is required in 'choices'"
        )
