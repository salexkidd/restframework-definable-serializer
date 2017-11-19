from django.http import Http404

from rest_framework.response import Response
from rest_framework import serializers
from rest_framework import mixins

from .renderers import TemplateHTMLPickupSerializerRenderer


class CreatePickupSerializerMixin(mixins.CreateModelMixin):
    def create(self, request, *args, **kwargs):

        instance = None
        try:
            instance = self.get_object()
        except Http404:
            ...

        response = None
        if instance:
            response = super().update(request, *args, **kwargs)
        else:
            response = super().create(request, *args, **kwargs)

        return response

    def perform_create(self, serializer):
        raise NotImplemented()


class RetrievePickupSerializerMixin(mixins.RetrieveModelMixin):
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        data = self.get_data_store_field_from_instance()
        serializer = self.get_serializer(data)
        return Response(serializer.data)


class UpdatePickupSerializerMixin(mixins.UpdateModelMixin):
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        data = self.get_data_store_field_from_instance()
        if partial:
            data.update(request.data)
        else:
            data = request.data

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def perform_update(self, serializer):
        instance = self.get_object()
        instance.__dict__[self.data_store_field_name] = serializer.validated_data
        instance.save()


class ListPickupSerializerModelMixin(object):

    def serializer_class_for_list(self):
        class SerializerForList(serializers.ModelSerializer):
            class Meta:
                model = self.get_queryset().model
                fields = '__all__'

        return SerializerForList

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer_class = self.serializer_class_for_list()

        if page is not None:
            serializer = serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = serializer_class(queryset, many=True)
        return Response(serializer.data)
