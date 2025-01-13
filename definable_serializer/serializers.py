from django.conf import settings as dj_settings
from django.core.exceptions import ValidationError
from django.utils.translation import get_language
from rest_framework import serializers as rf_serializers

try:
    from django.utils.translation import ugettext_lazy as _
except ImportError:
    from django.utils.translation import gettext_lazy as _

import codecs
import copy
import pprint
import pydoc
import types
import warnings

import dateparser
import simplejson
import yaml

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

STR_TO_DATETIME_MAP = {
    rf_serializers.DateField: lambda x: x.date() if x else None,
    rf_serializers.TimeField: lambda x: x.time() if x else None,
    rf_serializers.DateTimeField: lambda x: x if x else None,
}


BASE_CLASSES_BY_SETTINGS = list()
for c in getattr(dj_settings, "DEFINABLE_SERIALIZER_SETTINGS", {}).get("BASE_CLASSES", []):
    kls = pydoc.locate(c)
    if not kls:
        raise ValidationError("cannot find name '{}'".format(c))
    BASE_CLASSES_BY_SETTINGS.append(kls)


class TranslationMixin:

    @classmethod
    def _get_translate_string(metacls, field_defn, field_name, field_class,
                              language="default", raise_exception=False):

        def _get_or_default(v, target):
            trans_text = None
            if isinstance(v, dict):
                trans_text = v.get(language, None) or v.get("default", None)
                if trans_text is None and raise_exception:
                    raise ValidationError({
                        field_name: "'{}' is required in '{}'".format(
                            language, target)
                    })
            return trans_text

        field_args = field_defn.get("field_args", {})
        field_kwargs = field_defn.get("field_kwargs", {})

        result = dict()

        # label and help_text
        for target in ("label", "help_text", "initial"):
            trans_text = _get_or_default(
                field_kwargs.get(target, None), target)
            if trans_text:
                result[target] = trans_text

        # initial
        target = "initial"
        trans_text = _get_or_default(field_kwargs.get(target, None), target)
        if trans_text and issubclass(field_class, rf_serializers.CharField):
            result[target] = trans_text

        # placeholder
        target = "placeholder"
        value = field_kwargs.get("style", {}).get(target, None)
        trans_text = _get_or_default(value, target)
        if trans_text:
            result[target] = trans_text

        # choices
        target = "choices"
        can_trans_choices = all([
            len(field_defn.get("field_args", [])),
            not issubclass(field_class, rf_serializers.FilePathField),
            issubclass(field_class, rf_serializers.ChoiceField),
        ])
        if can_trans_choices:
            new_choice_list = list()
            for i, choice in enumerate(field_args[0]):
                choice_value, choice_label = choice[0], choice[1]
                trans_text = _get_or_default(choice_label, target)
                if trans_text:
                    choice_label = trans_text
                new_choice_list.append((choice_value, choice_label))

            result[target] = new_choice_list

        return result


class DefinableSerializerMeta(rf_serializers.SerializerMetaclass,
                              TranslationMixin):
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
    def _build_fields(metacls, fields_defn, serializer_classes,
                      allow_validate_method):
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

        def _convert_str_to_datetime(field_name, datetime_str):
            datetime_str = str(datetime_str)
            if not datetime_str:
                return None
            try:
                parser_settings = dict()
                if getattr(dj_settings, "USE_TZ", None):
                    ...
                    # parser_settings = {
                    #     "TIMEZONE": getattr(dj_settings, "TIME_ZONE", None),
                    #     "RETURN_AS_TIMEZONE_AWARE": True
                    # }
                from dateutil.parser import parse
                return parse(datetime_str)
                # return dateparser.parse(
                #     datetime_str, settings=parser_settings)

            except Exception as e:
                msg = f"Can't parser date or time format: value: {datetime_str} error: {e}"
                raise ValidationError({field_name: msg})

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

            # set trans result(label, help_text, placeholder, choices)
            trans_dict = metacls._get_translate_string(
                defn, field_name, field_class, raise_exception=True)

            for target in ("label", "help_text",):
                trans_text = trans_dict.get(target, None)
                if trans_text:
                    field_kwargs[target] = trans_text

            trans_text = trans_dict.get("placeholder", None)
            if trans_text:
                field_kwargs["style"]["placeholder"] = trans_text

            trans_choices = trans_dict.get("choices", None)
            if trans_choices:
                field_args[0] = trans_choices

            if defn.get("field", None) in ["MultipleChoiceField", "ChoiceField",]:
                field_kwargs["choices"] = field_args[0]
                field_kwargs["style"] = {
                    'inline': field_kwargs.get("inline", False),
                }
                del field_kwargs["inline"]
                field_args.pop(0)


            validators = _build_validators(defn)
            if validators:
                field_kwargs["validators"] = validators

            # convert str to object when Dates Field
            if issubclass(field_class, tuple(STR_TO_DATETIME_MAP.keys())):
                field_kwargs["initial"] = STR_TO_DATETIME_MAP[field_class](
                    _convert_str_to_datetime(
                        field_name, field_kwargs.get("initial", "")))

            # create field class
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

            allow_validate_method_violation = all([
                allow_validate_method is False,
                field_validate_method is not None,
            ])

            if allow_validate_method_violation:
                raise ValidationError({
                    field_name: "serializer validate_method not allowed."
                })

            if field_validate_method:
                try:
                    validate_methods.update({
                        field_name: metacls._parse_validate_method(
                            field_validate_method)
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

        allow_validate_method_violation = all([
            allow_validate_method is False,
            serializer_validate_method is not None
        ])

        if allow_validate_method_violation:
            raise ValidationError("serializer validate_method not allowed.")

        if serializer_validate_method:
            try:
                namespace.update({
                    "validate": metacls._parse_validate_method(
                        serializer_validate_method)
                })

            except Exception as e:
                msg = "Can't parse serializer_validate_method: {}"
                raise ValidationError({field_name: msg.format(e)})

        kls = super().__new__(
            metacls, serializer_name, bases, namespace, *kwargs)

        setattr(kls, "serializer_definition_data", serializer_defn)
        return kls

    def __init__(cls, name, bases, namespace, **kwargs):
        super().__init__(name, bases, namespace)

def _defn_pre_checker(defn_data):
    def _field_checker(defn):
        check_keys = ("name", "field",)
        for field in defn:
            for key in check_keys:
                if key not in field:
                    msg = "No {} in field: {}".format(
                        key, pprint.pformat(field))
                    raise ValidationError(msg)

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


class BaseDefinableSerializer(rf_serializers.Serializer, TranslationMixin):

    def trans_text(self, **kwargs):
        request = kwargs.get("context", {}).get("request", {})
        lang = getattr(request, "LANGUAGE_CODE", get_language())

        for field_defn in self.serializer_definition_data["fields"]:
            field_name = field_defn["name"]
            field = self.fields[field_name]
            field_class = field.__class__

            trans_dict = self.__class__._get_translate_string(
                field_defn, field_name, field_class, language=lang)

            # label and help_text
            for target in ("label", "help_text",):
                trans_text = trans_dict.get(target, None)
                if trans_text:
                    setattr(field, target, trans_text)

            # initial
            target = "initial"
            trans_text = trans_dict.get(target, None)
            if trans_text and issubclass(field_class, rf_serializers.CharField):
                setattr(field, target, trans_text)

            # placeholder
            target = "placeholder"
            trans_text = trans_dict.get(target, None)
            if trans_text:
                field.style["placeholder"] = trans_text

            # choices
            trans_choices = trans_dict.get("choices", None)
            if trans_choices:
                field._set_choices(trans_choices)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.trans_text(**kwargs)


def build_serializer(defn_data,
                     base_classes=list(),
                     allow_validate_method=True):

    def _build_serializer_class(serializer_defn):
        kwargs = {
            "serializer_classes": serializer_classes,
            "allow_validate_method": allow_validate_method,
        }

        serializer_name = serializer_defn["name"]

        namespace = {
            "namespace": DefinableSerializerMeta.__prepare__(
                serializer_name, _base_classes, **kwargs)
        }

        try:
            return DefinableSerializerMeta(
                serializer_defn, _base_classes, **namespace, **kwargs)
        except Exception as e:
            raise e

    _base_classes = tuple(
        [BaseDefinableSerializer, ] + BASE_CLASSES_BY_SETTINGS + base_classes
    )

    serializer_classes = dict()

    _defn_pre_checker(defn_data)

    main_defn = defn_data.get("main")
    depending_defn = defn_data.get("depending_serializers", list())

    main_serializer = None

    # build depending_serializers
    # try:
    #     for defn in depending_defn:
    #         serializer_classes[defn["name"]] = _build_serializer_class(defn)

    #     # build main serializer
    #     main_serializer = _build_serializer_class(main_defn)

    # except Exception as e:
    #     raise ValidationError(e)

    for defn in depending_defn:
        try:
            serializer_classes[defn["name"]] = _build_serializer_class(defn)
        except Exception as e:
            raise ValidationError(e)

    # build main serializer
    try:
        main_serializer = _build_serializer_class(main_defn)
    except Exception as e:
        raise ValidationError(e)

    return main_serializer


def build_serializer_by_json(json_data,
                             base_classes=list(),
                             allow_validate_method=True):

    return build_serializer(
        simplejson.loads(json_data),
        base_classes=base_classes,
        allow_validate_method=allow_validate_method,
    )


def build_serializer_by_json_file(json_file_path,
                                  base_classes=list(),
                                  allow_validate_method=True):

    with open(json_file_path, "rb") as fh:
        reader = codecs.getreader("utf-8")
        return build_serializer(
            simplejson.load(reader(fh)),
            base_classes=base_classes,
            allow_validate_method=allow_validate_method,
        )


def build_serializer_by_yaml(yaml_data,
                             base_classes=list(),
                             allow_validate_method=True):

    return build_serializer(
        yaml.load(yaml_data, Loader=yaml.SafeLoader),
        base_classes=base_classes,
        allow_validate_method=allow_validate_method,
    )


def build_serializer_by_yaml_file(yaml_file_path,
                                  base_classes=list(),
                                  allow_validate_method=True):

    with open(yaml_file_path, "rb") as fh:
        reader = codecs.getreader("utf-8")
        return build_serializer(
            yaml.load(reader(fh), Loader=yaml.SafeLoader),
            base_classes=base_classes,
            allow_validate_method=allow_validate_method,
        )
