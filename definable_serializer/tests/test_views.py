from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase
try:
    from django.urls import reverse
except ModuleNotFoundError as e:
    from django.core.urlresolvers import reverse

from rest_framework import status as http_status
from rest_framework.test import (
    APIRequestFactory, force_authenticate, APIClient
)

from ..tests.for_test import models as for_test_models
from copy import deepcopy

from definable_serializer.tests.for_test import models as for_test_models


class BaseViewTest(TestCase):
    def response_test(self, response, test_data):
        content_str = response.content.decode("utf-8")
        self.assertEqual(response.status_code, test_data["response_status"])

        if test_data["renderer_class_name"]:
            self.assertEqual(
                response.accepted_renderer.__class__.__name__,
                test_data["renderer_class_name"]
            )

        for correct_str in test_data["correct_contents"]:
            self.assertTrue(correct_str in content_str)

class TestAdminDetail(BaseViewTest):
    fixtures = ["test_fixture.json"]

    def setUp(self, *args, **kwargs):
        self.user = get_user_model().objects.create_user(
            username='one',
            email='one@example.com',
            password='top_secret',
            is_superuser=True,
            is_staff=True,
        )
        self.client = APIClient()
        self.client.login(username="one", password="top_secret")

    def test_access(self):
        url = reverse(
            "admin:for_test_paper_change",
            args=(1,)
        )
        response = self.client.get(url, follow=True)
        test_data = {
            "renderer_class_name": None,
            "correct_contents": [
                'Show Restframework Browsable Page',
                'email = EmailField()',
            ],
            "response_status": http_status.HTTP_200_OK
        }
        self.response_test(response, test_data)


class TestShowSerializerInfo(BaseViewTest):
    fixtures = ["test_fixture.json"]

    def setUp(self, *args, **kwargs):
        self.user = get_user_model().objects.create_user(
            username='one',
            email='one@example.com',
            password='top_secret',
            is_superuser=True,
            is_staff=True,
        )

        self.client = APIClient()
        self.client.login(username="one", password="top_secret")

    def test_access(self):
        url = reverse(
            "admin:show-browsable-api-view",
            kwargs={
                "pk": 1,
                "field_name": "definition",
                "app_label": "for_test",
                "model_name": "answer",
            }
        ) + "?format=api"

        response = self.client.get(url, follow=True)
        test_data = {
            "renderer_class_name": "BrowsableAPIRenderer",
            "correct_contents": [
                'Django REST framework</title>',
                'Make a GET request on the Show Serializer Info resource with the format set to `api`',
            ],
            "response_status": http_status.HTTP_200_OK
        }
        self.response_test(response, test_data)

class TestPickupSerializer(BaseViewTest):

    fixtures = ["test_fixture.json"]
    view_name = "for_test:answer"

    test_answer_data = {
        "first_name": "John",
        "last_name": "Doe",
        "age": "20",
        "email": "test@example.com",
        "sex": "male",
        "type": "family",
    }

    def setUp(self, *args, **kwargs):
        self.user = get_user_model().objects.create_user(
            username='one',
            email='one@example.com',
            password='top_secret'
        )

        self.user_two = get_user_model().objects.create_user(
            username='two',
            email='two@example.com',
            password='top_secret'
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def get_url(self, request_format):
        url = reverse(
            "{}-detail".format(self.view_name),
            kwargs={'pickup_serializer': 1}
        )
        return url + "?format={}".format(request_format)

    def test_access_json_format(self):
        request_format = "json"
        url = self.get_url(request_format)

        ######################### create #########################
        test_data = {
            "renderer_class_name": "JSONRenderer",
            "correct_contents": [],
            "response_status": http_status.HTTP_201_CREATED
        }
        response = self.client.post(url, data=self.test_answer_data)
        self.response_test(response, test_data)

        ######################### retrieve #########################
        test_data = {
            "renderer_class_name": "JSONRenderer",
            "correct_contents": [],
            "response_status": http_status.HTTP_200_OK
        }

        response = self.client.get(url)
        self.response_test(response, test_data)

        ######################### update #########################
        test_data = {
            "renderer_class_name": "JSONRenderer",
            "correct_contents": [],
            "response_status": http_status.HTTP_200_OK
        }

        update_data = deepcopy(self.test_answer_data)
        update_data["last_name"] = "The Ripper",

        response = self.client.put(url, data=update_data)
        self.response_test(response, test_data)
        self.assertEqual(
            for_test_models.Answer.objects.get(pk=1).data["last_name"],
            "The Ripper"
        )

        ######################## update(Partial) #########################
        test_data = {
            "renderer_class_name": "JSONRenderer",
            "correct_contents": [],
            "response_status": http_status.HTTP_200_OK
        }
        response = self.client.patch(url, data={
            "last_name": "Manjiro",
        })
        self.response_test(response, test_data)
        self.assertEqual(
            for_test_models.Answer.objects.get(pk=1).data["last_name"],
            "Manjiro"
        )

        ######################## destroy #########################
        test_data = {
            "renderer_class_name": "JSONRenderer",
            "correct_contents": [],
            "response_status": http_status.HTTP_204_NO_CONTENT
        }
        response = self.client.delete(url)
        self.response_test(response, test_data)
        with self.assertRaises(ObjectDoesNotExist):
            for_test_models.Answer.objects.get(pk=1)

    def test_access_browsable_api(self):
        request_format = "api"
        url = self.get_url(request_format)

        test_data = {
            "renderer_class_name": "BrowsableAPIRenderer",
            "correct_contents": [
                '<input name="email" class="form-control" type="email"',
                '<form action="/for_test_app/answer/1/?format=api"',
                'method="POST" enctype="multipart/form-data"',
            ],
            "response_status": http_status.HTTP_404_NOT_FOUND
        }

        response = self.client.get(url)
        self.response_test(response, test_data)

    def test_access_corejson(self):
        request_format = "javascript"
        url = self.get_url(request_format)
        test_data = {
            "renderer_class_name": "SchemaJSRenderer",
            "correct_contents": [],
            "response_status": http_status.HTTP_404_NOT_FOUND
        }
        response = self.client.get(url)
        self.response_test(response, test_data)

    def test_access_html(self):
        request_format = "pickup-serializer-html"
        url = self.get_url(request_format)
        test_data = {
            "renderer_class_name": "TemplateHTMLPickupSerializerRenderer",
            "correct_contents": [
                '<h1>Input here</h1>\n<form action="./" method="POST">',
                '<label >Last name</label>',
                '<label >First name</label>',
            ],
            "response_status": http_status.HTTP_200_OK
        }
        response = self.client.get(url)
        self.response_test(response, test_data)

    def test_corejson_serializer_per_object(self):
        request_format = "corejson-pickup-serializer"
        url = self.get_url(request_format)
        test_data = {
            "renderer_class_name": "CoreJSONPickupSerializerRenderer",
            "correct_contents": [
                '"create":{"_type":"link","url":"/for_test_app/answer/1/"',
                '"action":"post","encoding":"application/json"',
            ],
            "response_status": http_status.HTTP_200_OK
        }
        response = self.client.get(url)
        self.response_test(response, test_data)

    def test_open_api_serializer_per_object_schema(self):
        request_format = "openapi-pickup-serializer-schema"
        url = self.get_url(request_format)
        test_data = {
            "renderer_class_name": "OpenAPIPickupSerializerSchemaRenderer",
            "correct_contents": [
                '{"swagger": "2.0", "info": {"title": "answer_view_set API",'
            ],
            "response_status": http_status.HTTP_200_OK
        }
        response = self.client.get(url)
        self.response_test(response, test_data)

    def test_swagger_ui_serializer_per_object(self):
        request_format = "swagger-pickup-serializer"
        url = self.get_url(request_format)
        test_data = {
            "renderer_class_name": "SwaggerUIPickupSerializerRenderer",
            "correct_contents": [
                '<!DOCTYPE html>\n<html>\n<head>\n',
                "<redoc spec-url=\'/for_test_app/answer/1/?format=openapi-pickup-serializer-schema\'>"
            ],
            "response_status": http_status.HTTP_404_NOT_FOUND
        }
        response = self.client.get(url)
        self.response_test(response, test_data)

    def test_list(self):
        # TODO: jsonじゃないとずっこけて死ぬのでテストする
        request_format = "json"
        url = reverse(
            "{}-list".format(self.view_name)
        ) + "?format={}".format(request_format)
        response = self.client.get(url)

        self.assertEqual(response.json()["count"], 0)

        paper = for_test_models.Paper.objects.get(pk=1)

        # create 2 ~ 11 object
        for i in range(2, 22):
            paper.id = None
            paper.save()
            for_test_models.Answer.objects.create(
                respondent=self.user,
                paper=paper,
                data=self.test_answer_data,
            )

        # and for user_two
        for_test_models.Answer.objects.create(
            respondent=self.user_two,
            paper=paper,
            data=self.test_answer_data,
        )

        # user one
        response = self.client.get(url)
        self.assertEqual(response.json()["count"], 20)
        self.assertEqual(
            response.json()["results"][0]["respondent"],
            {'id': 1, 'username': 'one', 'email': 'one@example.com'}
        )

        # user two
        self.client.force_authenticate(user=self.user_two)
        response = self.client.get(url)
        self.assertEqual(response.json()["count"], 1)
        self.assertEqual(
            response.json()["results"][0]["respondent"],
            {'id': 2, 'username': 'two', 'email': 'two@example.com'}
        )

        # paper serializers
        self.assertIn("definition", response.json()["results"][0]["paper"])
