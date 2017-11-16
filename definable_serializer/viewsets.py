from rest_framework import viewsets
from rest_framework.mixins import DestroyModelMixin

from .views import PickupSerializerGenericView
from definable_serializer.mixins import (
    CreatePickupSerializerMixin,
    RetrievePickupSerializerMixin,
    UpdatePickupSerializerMixin,
    ListPickupSerializerModelMixin,
)


class PickupSerializerGenericViewSet(viewsets.ViewSetMixin,
                                     PickupSerializerGenericView):
    ...


class ReadOnlyPickupSerializerViewSet(RetrievePickupSerializerMixin,
                                      ListPickupSerializerModelMixin,
                                      PickupSerializerGenericViewSet):
    ...


class PickupSerializerViewSet(CreatePickupSerializerMixin,
                              RetrievePickupSerializerMixin,
                              UpdatePickupSerializerMixin,
                              DestroyModelMixin,
                              ListPickupSerializerModelMixin,
                              PickupSerializerGenericViewSet):
    ...
