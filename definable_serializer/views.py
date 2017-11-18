try:
    from django.urls import resolve
except ModuleNotFoundError as e:
    from django.core.urlresolvers import resolve

from django.contrib.contenttypes.models import ContentType

from rest_framework import serializers, viewsets
from rest_framework.generics import (
    get_object_or_404, CreateAPIView, GenericAPIView
)
from rest_framework.response import Response


# TODO: Why use CreateAPIView? Maybe GenericAPIView???
class ShowSerializerInfo(CreateAPIView):
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


class PickupSerializerGenericView(GenericAPIView):
    serializer_queryset = None
    serializer_field_name = None
    data_store_field_name = None

    api_version = None
    api_name = None

    def get_api_name(self):
        return self.api_name

    def get_version(self):
        return self.api_version

    def get_queryset_for_serializer(self):
        return self.serializer_queryset

    def get_serializer_field_name(self):
        return self.serializer_field_name

    def get_unique_key_data(self):
        raise NotImplemented()

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        filter_kwargs = {self.lookup_field: self.kwargs["pickup_serializer"]}
        filter_kwargs.update(self.get_unique_key_data())

        obj = get_object_or_404(queryset, **filter_kwargs)
        self.check_object_permissions(self.request, obj)

        return obj

    def get_serializer_define_object(self):
        filer_key = self.lookup_field.split("__")[-1]
        filter_kwargs = {filer_key: self.kwargs["pickup_serializer"]}

        obj = get_object_or_404(
            self.get_queryset_for_serializer(), **filter_kwargs)

        # TODO: Permission check
        ...

        return obj

    def get_serializer_class(self):
        obj = self.get_serializer_define_object()
        get_serializer_func = getattr(
            obj, "get_{}_serializer_class".format(self.serializer_field_name))

        return get_serializer_func()
