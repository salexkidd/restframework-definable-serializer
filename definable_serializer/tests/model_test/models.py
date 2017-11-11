from django.db import models


from ... import models as definable_serializers_models


class TestModel(definable_serializers_models.AbstractDefinitiveSerializerModel):
    name = models.CharField()
