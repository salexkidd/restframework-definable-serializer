from django.db import models

from .fields import (
    DefinableSerializerByJSONField,
    DefinableSerializerByYAMLField,
)
from ..serializers import build_serializer

import re

get_serializer_regex = re.compile("^get_(.*)_serializer_class$")


__all__ = (
    "AbstractDefinitiveSerializerModel",
)


class AbstractDefinitiveSerializerModel(models.Model):

    def _get_serializer(self, field_name):
        def _func():
            return build_serializer(getattr(self, field_name))
        return _func

    def __getattr__(self, name):
        result = get_serializer_regex.match(name)
        if result:
            field_name = result.group(1)
            return self._get_serializer(field_name)

        type(self).__getattribute__(self, name)

    class Meta:
        abstract = True
