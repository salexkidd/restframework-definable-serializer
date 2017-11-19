from django.http import Http404
from django.shortcuts import render

from rest_framework.renderers import CoreJSONRenderer, TemplateHTMLRenderer
from rest_framework_swagger.renderers import (
    OpenAPIRenderer, OpenAPICodec,
)

import re
import coreapi
from drf_openapi.codec import SwaggerUIRenderer, OpenAPIRenderer
from drf_openapi.entities import OpenApiSchemaGenerator, OpenApiDocument

DEFAULT_NO_VERSION_STRING = "no-versioning"


class OpenAPIDocMixin(object):
    def camel_to_sneak(self, string):
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', string).lower()

    def get_openapi_doc(self, data, media_type=None, renderer_context=None):
        view = renderer_context["view"]
        request = renderer_context["request"]

        schema_gen = OpenApiSchemaGenerator(version=DEFAULT_NO_VERSION_STRING)
        content_dict = {
            action: schema_gen.get_link(request.path, method.upper(), view)
                for method, action in view.action_map.items()
        }

        opt = {
            "api_name": self.camel_to_sneak(view.__class__.__name__),
            "version": DEFAULT_NO_VERSION_STRING,
        }

        for attr in ("api_name", "version",):
            func_name = "get_{}".format(attr)
            opt[attr] = getattr(view, func_name, lambda: None)() or opt[attr]

        return OpenApiDocument(
            title="{} API".format(opt["api_name"]),
            description=view.__doc__ ,
            url=request.build_absolute_uri(),
            content={opt["api_name"]: content_dict},
            version=opt["version"]
        )


class CoreJSONPickupSerializerRenderer(OpenAPIDocMixin, CoreJSONRenderer):

    media_type = 'application/coreapi-pickup-serializer+json'
    format = 'corejson-pickup-serializer'

    def render(self, data, media_type=None, renderer_context=None):
        return coreapi.codecs.CoreJSONCodec().dump(
            self.get_openapi_doc(
                data, media_type=None, renderer_context=renderer_context),
            indent=bool(renderer_context.get('indent', 0))
        )


class OpenAPIPickupSerializerSchemaRenderer(OpenAPIDocMixin, OpenAPIRenderer):

    media_type = 'application/openapi-pickup-serializer-schema+json'
    format = 'openapi-pickup-serializer-schema'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        doc = self.get_openapi_doc(
            data, media_type=None, renderer_context=renderer_context)
        extra = self.get_customizations()
        return OpenAPICodec().encode(doc, extra=extra)


class SwaggerUIPickupSerializerRenderer(SwaggerUIRenderer):
    template = 'swagger_ui_serializer_per_object.html'
    format = 'swagger-pickup-serializer'


class TemplateHTMLPickupSerializerRenderer(TemplateHTMLRenderer):

    media_type = 'text/html'
    format = 'pickup-serializer-html'
    charset = 'utf-8'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        renderer_context = renderer_context or {}
        view = renderer_context['view']
        request = renderer_context['request']
        response = renderer_context['response']

        template_names = self.get_template_names(response, view)
        template = self.resolve_template(template_names)

        if hasattr(self, 'resolve_context'):
            context = self.resolve_context(data, request, response)
        else:
            context = self.get_template_context(data, renderer_context)

        return template.render(context, request=request)

    def get_template_context(self, data, renderer_context):
        view = renderer_context['view']
        request = renderer_context['request']
        response = renderer_context['response']

        instance = None
        serializer = None
        serializer_class = view.get_serializer_class()

        data = dict()
        try:
            data = view.get_data_store_field_from_instance()
        except Http404 as e:
            ...

        if request.method in ("POST", "PUT", "PATCH",):
            serializer = serializer_class(data=request.data)
            serializer.is_valid(raise_exception=False)

        else:
            try:
                instance = view.get_object()
                data = getattr(instance, view.data_store_field_name, {})
                serializer = serializer_class(data=data)
                serializer.is_valid(raise_exception=False)

            except Http404 as e:
                serializer = serializer_class()

        data["serializer"] = serializer
        data["instance"] = instance

        data.update(view.get_template_context())

        return data
