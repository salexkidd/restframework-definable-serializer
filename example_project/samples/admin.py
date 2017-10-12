from django.contrib import admin
from definable_serializer.admin import DefinableSerializerAdmin

from . import models as samples_models


@admin.register(samples_models.Sample)
class Sample(DefinableSerializerAdmin):
    ...
