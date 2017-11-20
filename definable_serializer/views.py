from django.contrib.contenttypes.models import ContentType

from rest_framework import serializers
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response


class ShowSerializerInfo(GenericAPIView):
    public = False

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        self._serializer_model = self._get_serializer_model()

    def _get_serializer_model(self):
        content = ContentType.objects.get(
            app_label=self.kwargs["app_label"],
            model=self.kwargs["model_name"]
        )
        return content.model_class()

    def get_object(self, *args, **kwargs):
        return {}

    def get_queryset(self, *args, **kwargs):
        return self._serializer_model.objects.all()

    def get_serializer_class(self, *args, **kwargs):
        try:
            field_name = self.kwargs["field_name"]
            pk = self.kwargs["pk"]
            instance = self._serializer_model.objects.get(pk=pk)
            func_name = "get_{}_serializer_class".format(
                self.kwargs["field_name"])
            serializer_class = kls = getattr(instance, func_name)()

        except Exception as e:
            serializer_class = serializers.Serializer

        return serializer_class

    def get(self, *args, **kwargs):
        return Response("Hello")

    def post(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        return Response(data=serializer.data)
