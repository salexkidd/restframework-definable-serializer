"""
Copyright 2017 salexkidd

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

from django.utils.translation import ugettext as _
from django.core.exceptions import ValidationError

from rest_framework import serializers as rf_serializers

import simplejson
import codecs
import pprint
import pydoc
import types
import yaml
import warnings
import copy

NOT_AVAILABLE_FIELDS = (
    rf_serializers.ListField,
    rf_serializers.DictField,
    rf_serializers.SerializerMethodField,
)


__all__ = (
    "build_serializer",
    "build_serializer_by_json",
    "build_serializer_by_json_file",
    "build_serializer_by_yaml",
    "build_serializer_by_yaml_file",
)


class DefinableSerializerMeta(rf_serializers.SerializerMetaclass):
    # https://stackoverflow.com/questions/27258557/metaclass-arguments-for-python-3-x

    @classmethod
    def _parse_validate_method(metacls, method_str):
        global_var, local_var = dict(), dict()

        try:
            exec(method_str, global_var, local_var)
            validate_method = local_var["validate_method"]

        except Exception as e:
            raise ValidationError(e)

        if not isinstance(validate_method, types.FunctionType):
            raise ValidationError("Not a function")

        return validate_method

    @classmethod
    def _get_field_class(metacls, field_class_str, serializer_classes):

        # get from Django Restframework serializers
        field_class = getattr(rf_serializers, field_class_str, None)

        # get from builded depending serializers
        if not field_class:
            field_class = serializer_classes.get(field_class_str, None)

        # You can get "<< package>>.<< module >>.<< class >>" string
        if not field_class:
            field_class = pydoc.locate(field_class_str)

        return field_class

    @classmethod
    def _build_fields(metacls, fields_defn, serializer_classes, allow_validate_method):
        fields = dict()
        validate_methods = dict()

        def _build_validators(defn):
            field_name = defn["name"]
            validators = list()

            for validator_defn in defn.get("validators", list()):
                validator_class_path = validator_defn["validator"]
                validator_class = pydoc.locate(validator_class_path)

                if not validator_class:
                    raise ValidationError({
                        field_name: "cannot import name '{}'".format(
                            validator_class_path
                        )
                    })

                try:
                    validators.append(
                        validator_class(
                            *validator_defn.get("args", list()),
                            **validator_defn.get("kwargs", dict())
                        )
                    )
                except Exception as e:
                    raise ValidationError({field_name: e})

            return validators

        for defn in fields_defn:
            field_class_str = defn["field"]
            field_name = defn["name"]

            field_args = copy.deepcopy(defn.get("field_args", list()))
            field_kwargs = copy.deepcopy(defn.get("field_kwargs", dict()))

            field_class = metacls._get_field_class(
                field_class_str, serializer_classes)

            if field_class in NOT_AVAILABLE_FIELDS:
                e_str = "'{}' field not avalable.".format(field_class_str)
                raise ValidationError({field_name: e_str})

            if not field_class:
                e_str = "Can't find '{}' field class".format(field_class_str)
                raise ValidationError({field_name: e_str})

            validators = _build_validators(defn)
            if validators:
                field_kwargs["validators"] = validators

            try:
                fields[field_name] = field_class(*field_args, **field_kwargs)

            except Exception as e:
                raise ValidationError({field_name: e})

            # Field validate method
            if defn.get("validate_method", None):
                warnings.warn(
                    "'validate_method' will be deprecated in the future. "
                    "Please change to field_validate_method.",
                    PendingDeprecationWarning
                )

            field_validate_method = defn.get(
                "validate_method", None
            ) or defn.get(
                "field_validate_method", None
            )

            if allow_validate_method == False and field_validate_method != None:
                raise ValidationError({
                    field_name: "serializer validate_method not allowed."
                })

            if field_validate_method:
                try:
                    validate_methods.update({
                        field_name: metacls._parse_validate_method(field_validate_method)
                    })

                except Exception as e:
                    e_str = "Can't parse {} field_validate_method: {}".format(
                        field_name, e)
                    raise ValidationError({field_name: e_str})

        return fields, validate_methods

    @classmethod
    def __prepare__(metacls, name, bases, **kwargs):
        return super().__prepare__(name, bases, **kwargs)

    def __new__(metacls, serializer_defn, bases, namespace, **kwargs):

        # serializer_name
        serializer_name = serializer_defn["name"]
        fields_defn = serializer_defn["fields"]
        serializer_classes = kwargs.pop("serializer_classes")
        allow_validate_method = kwargs.pop("allow_validate_method", True)

        # build fields
        fields, field_validate_methods = metacls._build_fields(
            fields_defn, serializer_classes, allow_validate_method)

        # set fields
        namespace.update(fields)

        # field validate methods
        for field_name, validate_method in field_validate_methods.items():
            method_name = "validate_{}".format(field_name)
            namespace.update({method_name: validate_method})

        # serializer validate method
        if serializer_defn.get("validate_method", None):
            warnings.warn(
                "'validate_method' will be deprecated in the future. "
                "Please change to serializer_validate_method.",
                PendingDeprecationWarning
            )

        serializer_validate_method = serializer_defn.get(
            "serializer_validate_method", None
        ) or serializer_defn.get(
            "validate_method", None
        )

        if allow_validate_method == False and serializer_validate_method != None:
            raise ValidationError("serializer validate_method not allowed.")

        if serializer_validate_method:
            try:
                namespace.update({
                    "validate": metacls._parse_validate_method(
                        serializer_validate_method)
                })

            except Exception as e:
                raise ValidationError({
                    field_name: "Can't parse serializer_validate_method: {}".format(e)
                })

        return super().__new__(
            metacls, serializer_name, bases, namespace, *kwargs)

    def __init__(cls, name, bases, namespace, **kwargs):
        super().__init__(name, bases, namespace)


def _defn_pre_checker(defn_data):

    def _field_checker(defn):
        check_keys = ("name", "field",)

        for field in defn:
            for key in check_keys:
                if key not in field:
                    raise ValidationError("No {} in field: {}".format(
                        key, pprint.pformat(field)))

    def _serializer_checker(defn):
        check_keys = ("name", "fields",)

        for key in check_keys:
            if key not in defn:
                e_str = "No {} in serializer definition: {}".format(
                    key, pprint.pformat(defn))
                raise ValidationError(e_str)

        _field_checker(defn["fields"])

    if "main" not in defn_data:
        raise ValidationError("Please define a 'main' serializer data")

    _serializer_checker(defn_data["main"])

    if "depending_serializers" in defn_data:
        for defn in defn_data["depending_serializers"]:
            _serializer_checker(defn)


class BaseDefinableSerializer(rf_serializers.Serializer):
    ...


def build_serializer(defn_data, allow_validate_method=True):

    def _build_serializer_class(serializer_defn):

        kwargs = {
            "serializer_classes": serializer_classes,
            "allow_validate_method":allow_validate_method,
        }

        serializer_name = serializer_defn["name"]

        namespace = {
            "namespace": DefinableSerializerMeta.__prepare__(
                serializer_name, _base_classes, **kwargs)
        }

        return DefinableSerializerMeta(
            serializer_defn, _base_classes, **namespace, **kwargs)

    _base_classes = (BaseDefinableSerializer,)
    serializer_classes = dict()

    _defn_pre_checker(defn_data)

    main_defn = defn_data.get("main")
    depending_defn = defn_data.get("depending_serializers", list())

    main_serializer = None

    # build depending_serializers
    try:
        for defn in depending_defn:
            serializer_classes[defn["name"]] = _build_serializer_class(defn)

        # build main serializer
        main_serializer = _build_serializer_class(main_defn)

    except Exception as e:
        raise ValidationError(e)

    return main_serializer


def build_serializer_by_json(json_data, allow_validate_method=True):
    return build_serializer(simplejson.loads(json_data), allow_validate_method)


def build_serializer_by_json_file(json_file_path, allow_validate_method=True):
    with open(json_file_path, "rb") as fh:
        reader = codecs.getreader("utf-8")
        return build_serializer(
            simplejson.load(reader(fh)),
            allow_validate_method
        )


def build_serializer_by_yaml(yaml_data, allow_validate_method=True):
    return build_serializer(yaml.load(yaml_data), allow_validate_method)


def build_serializer_by_yaml_file(yaml_file_path, allow_validate_method=True):
    with open(yaml_file_path, "rb") as fh:
        reader = codecs.getreader("utf-8")
        return build_serializer(yaml.load(reader(fh)), allow_validate_method)
