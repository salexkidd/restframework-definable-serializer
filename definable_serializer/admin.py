from django.contrib import admin
from django.conf.urls import url

from definable_serializer.models import AbstractDefinableSerializerField
from definable_serializer.views import ShowSerializerInfo


class DefinableSerializerAdmin(admin.ModelAdmin):
    change_form_template = "admin/definable_serializer/change_form.html"

    def __get_serializers(self, instance):
        serializers_dict = dict()

        for field in self.model._meta.fields:
            if isinstance(field, AbstractDefinableSerializerField):
                field_obj = getattr(instance, field.name)

                try:
                    serializer = getattr(
                        instance, "get_{}_serializer_class".format(field.name)
                    )()()
                    setattr(serializer, "serializer_name", serializer.__class__.__name__)
                    serializers_dict[field.name] = serializer

                except Exception as e:
                    ...

        return serializers_dict

    def change_view(self, request, object_id, form_url='', extra_context=None):
        instance = self.model.objects.get(pk=object_id)

        extra_context = extra_context or dict()
        extra_context["restframework_definable_serializers"] = self.__get_serializers(
            instance
        )
        return super().changeform_view(request, object_id, form_url, extra_context)

    def get_urls(self):
        urls = super().get_urls()
        return [
            url(
                r'(?P<app_label>.+)/(?P<model_name>.+)/(?P<pk>\d+)/(?P<field_name>.+)/show-browsable-api-view/$',
                self.admin_site.admin_view(ShowSerializerInfo.as_view()),
                name='show-browsable-api-view'
            ),
        ] + urls
