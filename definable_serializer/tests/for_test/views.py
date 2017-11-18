from django.contrib.auth import get_user_model

from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.exceptions import NotFound
from rest_framework import mixins as rf_mixins
from rest_framework import serializers


from . import models as for_test_models
from definable_serializer.viewsets import (
    PickupSerializerViewSet,
)


class AnswerViewSet(PickupSerializerViewSet):
    template_name = "test.html"
    lookup_field = "paper__pk"
    queryset = for_test_models.Answer.objects.all()

    serializer_queryset = for_test_models.Paper.objects.all()
    serializer_field_name = "definition"
    data_store_field_name = "data"

    def get_unique_key_data(self):
        return {"respondent": self.request.user}

    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(
            *args, **kwargs).filter(respondent=self.request.user)

    def serializer_class_for_list(self):
        class Respondent(serializers.ModelSerializer):
            class Meta:
                model = get_user_model()
                fields = ('id', 'username', 'email',)


        class PaperSerializer(serializers.ModelSerializer):
            class Meta:
                model = for_test_models.Paper
                fields = '__all__'


        class SerializerForList(serializers.ModelSerializer):
            paper = PaperSerializer()
            respondent = Respondent()

            class Meta:
                model = self.get_queryset().model
                fields = '__all__'

        return SerializerForList

    def perform_create(self, serializer):
        self.get_serializer_define_object()
        self.get_queryset().model.objects.create(
            respondent=self.request.user,
            paper=self.get_serializer_define_object(),
            **{self.data_store_field_name: serializer.validated_data}
        )
