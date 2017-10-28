"""
Copyright 2017 salexkidd

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

from django.contrib import admin
from django.conf.urls import url
from django.shortcuts import render_to_response
from django.template import RequestContext

from rest_framework.renderers import AdminRenderer

from definable_serializer.models import AbstractDefinableSerializerField
from definable_serializer.views import ShowSerializerInfo

from functools import update_wrapper


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
