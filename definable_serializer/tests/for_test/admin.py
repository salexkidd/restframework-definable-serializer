from django.contrib import admin

from . import models as for_test_models


admin.register(for_test_models.Paper)
class PaperAdmin(admin.ModelAdmin):
    ...


admin.register(for_test_models.Answer)
class AnswerAdmin(admin.ModelAdmin):
    ...
