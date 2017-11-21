from django.http import Http404

from rest_framework import status as http_status
from rest_framework.renderers import (
    CoreJSONRenderer, TemplateHTMLRenderer
)

import coreapi
from drf_openapi.codec import (
    SwaggerUIRenderer, OpenAPIRenderer, OpenAPICodec
)
from drf_openapi.entities import (
    OpenApiSchemaGenerator, OpenApiDocument
)
DEFAULT_NO_VERSION_STRING = "no-versioning"


class OpenAPIDocMixin(object):
    def get_openapi_doc(self, data, media_type=None, renderer_context=None):
        view = renderer_context["view"]
        request = renderer_context["request"]

        opt = {
            "api_name": view.__class__.__name__,
            "api_version": DEFAULT_NO_VERSION_STRING,
        }

        for attr in ("api_name", "api_version",):
            func_name = "get_{}".format(attr)
            opt[attr] = getattr(view, func_name, lambda: None)() or opt[attr]

        schema_gen = OpenApiSchemaGenerator(opt["api_version"])
        content_dict = {
            action: schema_gen.get_link(request.path, method.upper(), view)
                for method, action in view.action_map.items()
        }

        doc = OpenApiDocument(
            version=opt["api_version"],
            title="{} API".format(opt["api_name"]),
            description=view.__doc__,
            url=request.build_absolute_uri(),
            content={opt["api_name"]: content_dict},
        )

        return doc


class CoreJSONPickupSerializerRenderer(OpenAPIDocMixin, CoreJSONRenderer):

    format = 'corejson-pickup-serializer'

    def render(self, data, media_type=None, renderer_context=None):
        renderer_context["response"].status_code = http_status.HTTP_200_OK
        return coreapi.codecs.CoreJSONCodec().dump(
            self.get_openapi_doc(
                data, media_type=media_type, renderer_context=renderer_context),
            indent=bool(renderer_context.get('indent', 0))
        )


class OpenAPIPickupSerializerSchemaRenderer(OpenAPIDocMixin, OpenAPIRenderer):

    format = 'openapi-pickup-serializer-schema'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        doc = self.get_openapi_doc(
            data, media_type=None, renderer_context=renderer_context)
        extra = self.get_customizations()
        renderer_context["response"].status_code = http_status.HTTP_200_OK
        return OpenAPICodec().encode(doc, extra=extra)


class SwaggerUIPickupSerializerRenderer(SwaggerUIRenderer):

    template = 'swagger_ui_serializer_per_object.html'
    format = 'swagger-pickup-serializer'


class TemplateHTMLPickupSerializerRenderer(TemplateHTMLRenderer):

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

        renderer_context["response"].status_code = http_status.HTTP_200_OK
        return template.render(context, request=request)

    def get_template_context(self, data, renderer_context):
        view = renderer_context['view']
        request = renderer_context['request']
        response = renderer_context['response']

        instance = None
        try:
            instance = view.get_object()
        except Http404 as e:
            pass

        serializer = None
        serializer_class = view.get_serializer_class()

        # The browser form does not support the PUT & PATCH method.
        # http://jxck.hatenablog.com/entry/why-form-dosent-support-put-delete
        serializer_data = None
        if request.method in ("POST",):
            serializer_data = request.data
            serializer = serializer_class(data=serializer_data)

        else:
            try:
                serializer_data = view.get_store_data()
                serializer = serializer_class(data=serializer_data)
            except Http404 as e:
                serializer = serializer_class()

        if serializer_data:
            serializer.is_valid(raise_exception=False)

        data["serializer"] = serializer
        data["instance"] = instance
        data.update(view.get_template_context())

        return data
