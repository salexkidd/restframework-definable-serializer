"""
DefinableSerializer Serializer
"""
from django.utils.translation import ugettext as _
from django.core.exceptions import ValidationError

from rest_framework import serializers as rf_serializers

import simplejson
import codecs
import pprint
import pydoc
import yaml


NOT_AVAILABLE_FIELDS = (
    rf_serializers.ListField,
    rf_serializers.DictField,
    rf_serializers.SerializerMethodField,
)


__all__ = (
    "build_serializer",
)


class DefinableSerializerMeta(rf_serializers.SerializerMetaclass):
    # https://stackoverflow.com/questions/27258557/metaclass-arguments-for-python-3-x

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
    def _build_fields(metacls, fields_defn, serializer_classes):
        fields = dict()

        for defn in fields_defn:
            field_class_str = defn["field"]
            field_name = defn["name"]

            field_class = metacls._get_field_class(field_class_str, serializer_classes)

            if field_class in NOT_AVAILABLE_FIELDS:
                raise ValidationError({
                    field_name: "Sorry, '{}' field not avalable.".format(field_class_str)
                })

            if not field_class:
                raise ValidationError({
                    field_name: "Can't find '{}' field class".format(field_class_str)
                })

            field_args = defn.get("field_args" , list())
            field_kwargs = defn.get("field_kwargs", dict())

            try:
                fields[field_name] = field_class(*field_args, **field_kwargs)

            except Exception as e:
                raise ValidationError({field_name: e})

        return fields

    @classmethod
    def __prepare__(metacls, name, bases, **kwargs):
        return super().__prepare__(name, bases, **kwargs)

    def __new__(metacls, name, bases, namespace, **kwargs):
        namespace.update(
            metacls._build_fields(
                kwargs.pop("fields_defn"),
                kwargs.pop("serializer_classes")
            )
        )
        return super().__new__(metacls, name, bases, namespace, *kwargs)

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
                raise ValidationError("No {} in serializer definition: {}".format(
                    key, pprint.pformat(defn)))

        _field_checker(defn["fields"])

    if "main" not in defn_data:
        raise ValidationError("Please define a 'main' serializer data")

    _serializer_checker(defn_data["main"])

    if "depending_serializers" in defn_data:
        for defn in defn_data["depending_serializers"]:
            _serializer_checker(defn)


from rest_framework.fields import (  # NOQA # isort:skip
    CreateOnlyDefault, CurrentUserDefault, SkipField, empty
)

class BaseDefinableSerializer(rf_serializers.Serializer):
    ...


def build_serializer(defn_data):

    def _build_serializer_class(serializer_defn):

        kwargs = {
            "fields_defn": serializer_defn["fields"],
            "serializer_classes": serializer_classes,
        }

        serializer_name = serializer_defn["name"]

        namespace = {
            "namespace": DefinableSerializerMeta.__prepare__(
                serializer_name, _base_classes, **kwargs)
        }

        return DefinableSerializerMeta(
            serializer_name, _base_classes, **namespace, **kwargs)

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


def build_serializer_by_json(json_data):
    return build_serializer(simplejson.loads(json_data))


def build_serializer_by_json_file(json_file_path):
    with open(json_file_path, "rb") as fh:
        reader = codecs.getreader("utf-8")
        return build_serializer(simplejson.load(reader(fh)))


def build_serializer_by_yaml(yaml_data):
    return build_serializer(yaml.load(yaml_data))


def build_serializer_by_yaml_file(yaml_file_path):
    with open(yaml_file_path, "rb") as fh:
        reader = codecs.getreader("utf-8")
        return build_serializer(yaml.load(reader(fh)))
