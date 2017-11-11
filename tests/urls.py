from django.conf.urls import url, include
from django.contrib import admin

from rest_framework.schemas import get_schema_view
from rest_framework.documentation import include_docs_urls

# from definable_serializer.views import OpenAPISchemaWithoutVersion

schema_view = get_schema_view(title='Example')

urlpatterns = [
    url(r'^schema/$', schema_view),
    url(r'^docs/', include_docs_urls(title='API Docs')),
    # url(r'open-api/schema', OpenAPISchemaWithoutVersion.as_view(), name="api_schema"),
    url(
        r'^for_test_app/',
        include(
            "definable_serializer.tests.for_test.urls",
            namespace='for_test'
        )
    )
]
