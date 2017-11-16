from django.conf.urls import url, include
from django.contrib import admin

from rest_framework.schemas import get_schema_view
from rest_framework.documentation import include_docs_urls

urlpatterns = [
    url(
        r'^for_test_app/',
        include(
            "definable_serializer.tests.for_test.urls",
            namespace='for_test'
        )
    )
]
