from . import models as for_test_models

from django.contrib import admin


admin.register(for_test_models.Paper)
class PaperAdmin(admin.ModelAdmin):
    ...


admin.register(for_test_models.Answer)
class AnswerAdmin(admin.ModelAdmin):
    ...
