from django.contrib import admin
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect

from definable_serializer.models import (
    DefinableSerializerByJSONField,
    DefinableSerializerByYAMLField,
)

csrf_protect_m = method_decorator(csrf_protect)


definable_serializer_classes = (
    DefinableSerializerByJSONField,
    DefinableSerializerByYAMLField,
)


class DefinableSerializerAdmin(admin.ModelAdmin):
    change_form_template = "admin/definable_serializer/change_form.html"

    def change_view(self, request, object_id, form_url='', extra_context=None):

        extra_context = extra_context or dict()
        extra_context["drf_definable_serializers"] = dict()

        instance = self.model.objects.get(pk=object_id)

        for field in self.model._meta.fields:
            if any([isinstance(field, kls) for kls in definable_serializer_classes]):
                field_obj = getattr(instance, field.name)
                serializer = getattr(
                    instance, "get_{}_serializer_class".format(field.name)
                )()()
                extra_context["drf_definable_serializers"][field.name] = serializer
        return super().changeform_view(request, object_id, form_url, extra_context)
