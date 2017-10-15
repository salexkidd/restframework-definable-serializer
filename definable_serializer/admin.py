from django.contrib import admin
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect

from definable_serializer.models import AbstractDefinableSerializerField


class DefinableSerializerAdmin(admin.ModelAdmin):
    change_form_template = "admin/definable_serializer/change_form.html"

    def change_view(self, request, object_id, form_url='', extra_context=None):

        extra_context = extra_context or dict()
        extra_context["restframework_definable_serializers"] = dict()

        instance = self.model.objects.get(pk=object_id)

        for field in self.model._meta.fields:
            if isinstance(field, AbstractDefinableSerializerField):
                field_obj = getattr(instance, field.name)

                try:
                    serializer = getattr(
                        instance, "get_{}_serializer_class".format(field.name)
                    )()()
                    setattr(serializer, "serializer_name", serializer.__class__.__name__)
                    extra_context["restframework_definable_serializers"][field.name] = serializer

                except Exception as e:
                    ...

        return super().changeform_view(request, object_id, form_url, extra_context)
