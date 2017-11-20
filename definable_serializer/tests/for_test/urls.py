from django.conf.urls import url, include
from . import views as for_test_views

from definable_serializer.contrib.pickup_serializer.routers import(
    PickupSerializerRouter
)

router = PickupSerializerRouter()
router.register(r"answer", for_test_views.AnswerViewSet, "answer")

urlpatterns = router.urls
