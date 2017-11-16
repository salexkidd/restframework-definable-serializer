from django.shortcuts import render

from rest_framework.renderers import CoreJSONRenderer
from rest_framework_swagger.renderers import (
    OpenAPIRenderer, OpenAPICodec,
)

import coreapi
from drf_openapi.codec import SwaggerUIRenderer
from drf_openapi.entities import (
    OpenApiSchemaGenerator, OpenApiDocument,
)
from drf_openapi.codec import OpenAPIRenderer

DEFAULT_NO_VERSION_STRING = "no-versioning"

_METHOD_MAPPING = {
    "GET": "retrieve",
    "POST": "create",
    "PUT": "update",
    "PATCH": "update",
}


class OpenAPIDocsMixin(object):
    def get_openapi_docs(self, data, media_type=None, renderer_context=None):
        request = renderer_context.get("request", None)
        view = renderer_context.get("view", None)

        schema_gen = OpenApiSchemaGenerator(
            version=DEFAULT_NO_VERSION_STRING)

        content_dict = dict()
        for method in view.allowed_methods:
            if method in _METHOD_MAPPING.keys():
                content_dict[_METHOD_MAPPING[method]] = schema_gen.get_link(
                    request.path, method, view)

        view_class_name = view.__class__.__name__
        return OpenApiDocument(
            title="{} API".format(view_class_name),
            description=view.__doc__,
            url=request.build_absolute_uri(),
            content={view_class_name.lower(): content_dict},
            version=DEFAULT_NO_VERSION_STRING
        )


class CoreJSONSerializerPerObjectRenderer(OpenAPIDocsMixin, CoreJSONRenderer):
    media_type = 'application/coreapi-serializer-per-object+json'
    format = 'corejson-serializer-per-object'

    def render(self, data, media_type=None, renderer_context=None):
        docs = self.get_openapi_docs(
            data, media_type=None, renderer_context=renderer_context)
        indent = bool(renderer_context.get('indent', 0))
        codec = coreapi.codecs.CoreJSONCodec()
        return codec.dump(docs, indent=indent)


class OpenAPISerializerPerObjectSchemaRenderer(OpenAPIDocsMixin, OpenAPIRenderer):
    media_type = 'application/openapi-serializer-per-object-schema+json'
    format = 'openapi-serializer-per-object-schema'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        docs = self.get_openapi_docs(
            data, media_type=None, renderer_context=renderer_context)
        extra = self.get_customizations()
        return OpenAPICodec().encode(docs, extra=extra)


class SwaggerUISerializerPerObjectRenderer(SwaggerUIRenderer):
    template = 'swagger_ui_serializer_per_object.html'
    media_type = 'application/swagger-serializer-per-object+json'
    format = 'swagger-serializer-per-object'
