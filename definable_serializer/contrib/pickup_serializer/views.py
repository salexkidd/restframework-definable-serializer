try:
    from django.urls import resolve
except ModuleNotFoundError as e:
    from django.core.urlresolvers import resolve

from rest_framework import serializers, viewsets
from rest_framework.generics import (
    get_object_or_404, CreateAPIView, GenericAPIView
)


class PickupSerializerGenericView(GenericAPIView):
    serializer_queryset = None
    serializer_field_name = None
    data_store_field_name = None

    api_version = None
    api_name = None

    def get_api_name(self):
        return self.api_name

    def get_api_version(self):
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

    def get_store_data(self):
        instance = self.get_object()
        return getattr(instance, self.data_store_field_name)

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

    def get_template_context(self):
        return {}
