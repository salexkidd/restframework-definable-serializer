from django.db import models
from django.test import TestCase

from ..models.compat import YAMLField


class TestYAMLModel(models.Model):
    yaml_field = YAMLField()


class TestYAMLField(TestCase):
    ...

    def test_to_python(self):
        yaml_data = """
        main:
          - 1
          - 2
          - 3
        """
        yaml_field = YAMLField()
        yaml_field.to_python(yaml_data)

        yaml_data = ""
        yaml_field = YAMLField()
        self.assertEqual(None, yaml_field.to_python(yaml_data))

        yaml_data = """`"""
        yaml_field = YAMLField()
        with self.assertRaises(Exception):
            yaml_field.to_python(yaml_data)

    def test_get_prep_value(self):
        yaml_field = YAMLField()
        self.assertEqual("", yaml_field.get_prep_value(None))

        yaml_field = YAMLField()
        data = {"aaa": "aaa😺",}

        self.assertEqual(
            "aaa: aaa😺\n",
            yaml_field.get_prep_value(data)
        )
