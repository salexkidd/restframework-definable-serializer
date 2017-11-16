from django.conf.urls import url, include
from django.contrib import admin


urlpatterns = [
    url(
        r'^for_test_app/',
        include(
            "definable_serializer.tests.for_test.urls",
            namespace='for_test'
        )
    )
]
