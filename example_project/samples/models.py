from django.db import models
from jsonfield.fields import JSONField

from definable_serializer.models import (
    DefinableSerializerByJSONField,
    DefinableSerializerByYAMLField,
    AbstractDefinitiveSerializerModel,
)


class Sample(AbstractDefinitiveSerializerModel):
    sample_one = DefinableSerializerByYAMLField()
    sample_two = DefinableSerializerByJSONField()
