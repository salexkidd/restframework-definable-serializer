from django.contrib import admin

from . import models as for_test_models
from definable_serializer.admin import DefinableSerializerAdmin


@admin.register(for_test_models.Paper)
class PaperAdmin(DefinableSerializerAdmin):
    ...


@admin.register(for_test_models.Answer)
class AnswerAdmin(DefinableSerializerAdmin):
    ...
