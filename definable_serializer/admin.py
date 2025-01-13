from django.contrib import admin

try:
    from django.conf.urls import url
except ImportError:
    from django.urls import re_path as url

from functools import update_wrapper

from django.shortcuts import get_object_or_404
from django.template import RequestContext
from rest_framework.renderers import AdminRenderer

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
                    print(e)

        return serializers_dict

    def change_view(self, request, object_id, form_url='', extra_context=None):
        instance = get_object_or_404(self.model, pk=object_id)
        extra_context = extra_context or dict()
        extra_context["restframework_definable_serializers"] = self.__get_serializers(
            instance
        )
        print(extra_context["restframework_definable_serializers"])
        return super().changeform_view(request, object_id, form_url, extra_context)

    def get_urls(self):
        info = self.model._meta.app_label, self.model._meta.model_name
        urls = super().get_urls()

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            wrapper.model_admin = self
            return update_wrapper(wrapper, view)

        return [
            url(
                r'(?P<pk>\d+)/(?P<field_name>.+)/show-browsable-api-view/$',
                self.admin_site.admin_view(ShowSerializerInfo.as_view()),
                name='%s_%s_show-browsable-api-view' % info
            ),

        ] + urls
