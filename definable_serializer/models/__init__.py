from django.db import models

from .fields import AbstractDefinableSerializerField
from ..serializers import build_serializer

import re

from .fields import * # no-qa


get_serializer_regex = re.compile("^__get_(.*)_serializer_class$")


__all__ = (
    "AbstractDefinitiveSerializerModel",
)


class AbstractDefinitiveSerializerModel(models.Model):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__get_class_serialier_methods()

    def __get_class_serialier_methods(self):
        for field in self._meta.fields:
            method_name = "get_{}_serializer_class".format(field.name)
            if isinstance(field, AbstractDefinableSerializerField):
                setattr(self, method_name, getattr(self, "__" + method_name))

    def _get_serializer(self, field_name):
        def _func():
            field = self._meta.get_field(field_name)
            defn = getattr(self, field_name)
            allow_validate_method = getattr(field, "allow_validate_method", False)
            base_classes = getattr(field, "base_classes", list())

            return build_serializer(
                defn,
                base_classes=base_classes,
                allow_validate_method=allow_validate_method,
            )

        return _func

    def __getattr__(self, name):
        result = get_serializer_regex.match(name)
        if result:
            field_name = result.group(1)
            return self._get_serializer(field_name)

        type(self).__getattribute__(self, name)

    class Meta:
        abstract = True
