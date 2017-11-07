try:
    from django.urls import resolve
except ModuleNotFoundError as e:
    from django.core.urlresolvers import resolve

from django.contrib.contenttypes.models import ContentType

from rest_framework import generics
from rest_framework.response import Response


class ShowSerializerInfo(generics.CreateAPIView):

    def dispatch(self, *args, **kwargs):
        self._url_data = resolve(self.request.path)
        self._serializer_model = self._get_serializer_model()
        return super().dispatch(*args, **kwargs)

    def get(self, *args, **kwargs):
        return "Hello"

    def _get_serializer_model(self):
        app_label, model_name, view_name = self._url_data.url_name.split("_")
        content = ContentType.objects.get(app_label=app_label, model=model_name)
        return content.model_class()

    def get_object(self, *args, **kwargs):
        return {}

    def get_queryset(self, *args, **kwargs):
        return self._serializer_model.objects.all()

    def get_serializer_class(self, *args, **kwargs):
        field_name = self._url_data.kwargs["field_name"]
        pk = self._url_data.kwargs["pk"]
        instance = self._serializer_model.objects.get(pk=pk)
        func_name = "get_{}_serializer_class".format(
            self._url_data.kwargs["field_name"]
        )
        return getattr(instance, func_name)()

    def get(self, *args, **kwargs):
        return Response("Hello")

    def post(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        return Response(data=serializer.data)
