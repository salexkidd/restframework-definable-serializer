from django.shortcuts import render

from rest_framework.renderers import CoreJSONRenderer
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
