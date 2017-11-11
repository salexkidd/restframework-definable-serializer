from django.db import models
from django.conf import settings

from definable_serializer.models import (
    DefinableSerializerByJSONField,
    DefinableSerializerByYAMLField,
    AbstractDefinitiveSerializerModel,
)
from definable_serializer.models.compat import (
    YAMLField as CompatYAMLField,
)


class Paper(AbstractDefinitiveSerializerModel):
    definition = DefinableSerializerByYAMLField()


class Answer(models.Model):

    respondent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    paper = models.ForeignKey(
        Paper,
        null=False,
    )

    data = CompatYAMLField()

    create_at = models.DateTimeField(
        null=False,
        blank=False,
        auto_now_add=True,
        auto_now=False,
    )

    update_at = models.DateTimeField(
        null=False,
        blank=False,
        auto_now=True,
    )

    class Meta:
        unique_together = ("paper", "respondent",)
