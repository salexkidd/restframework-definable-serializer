from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.exceptions import NotFound

from . import models as for_test_models
from definable_serializer.views import (
    PickupSerializerGenericView,
    PickupSerializerGenericViewSet
)

from rest_framework import mixins as rf_mixins


class AnswerViewSet(rf_mixins.CreateModelMixin,
                    rf_mixins.RetrieveModelMixin,
                    rf_mixins.UpdateModelMixin,
                    rf_mixins.ListModelMixin,
                    rf_mixins.DestroyModelMixin,
                    PickupSerializerGenericViewSet):

    template_name = "test.html"
    lookup_field = "paper__pk"
    queryset = for_test_models.Answer.objects.all()

    serializer_queryset = for_test_models.Paper.objects.all()
    serializer_field_name = "definition"
    store_data_field_name = "data"

    def get_unique_key_data(self):
        return {"respondent": self.request.user}

    #################### TODO: Mixin作らないとだめ ######################
    def perform_create(self, serializer):
        self.get_serializer_define_object()
        for_test_models.Answer.objects.create(
            respondent=self.request.user,
            paper=self.get_serializer_define_object(),
            **{self.store_data_field_name: serializer.validated_data}
        )

    #################### TODO: Mixin作らないとだめ ######################
    def retrieve(self, request, *args, **kwargs):
        # TODO: Mixin作らないとだめ
        instance = self.get_object()
        serializer = self.get_serializer(
            getattr(instance, self.store_data_field_name)
        )
        return Response(serializer.data)

    #################### TODO: Mixin作らないとだめ ######################
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        data = instance.data
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
        instance.__dict__[self.store_data_field_name] = serializer.validated_data
        instance.save()
