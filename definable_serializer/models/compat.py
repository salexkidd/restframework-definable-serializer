"""
Copyright 2017 salexkidd

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

from django.core.exceptions import ValidationError
from django.core.serializers.json import DjangoJSONEncoder

import six
import ruamel.yaml as ruamel_yaml
from yamlfield.fields import YAMLField as OriginalYAMLField
from jsonfield.fields import JSONField as OriginalJSONField


class YAMLField(OriginalYAMLField):

    def _unicode_dump(self, value):
        value = ruamel_yaml.dump(
            value,
            Dumper=ruamel_yaml.RoundTripDumper,
            default_flow_style=False,
            allow_unicode = True,
        )
        return value

    def to_python(self, value):
        if value == "":
            return None
        try:
            if isinstance(value, six.string_types):
                return ruamel_yaml.load(value, ruamel_yaml.RoundTripLoader)
        except Exception as e:
            raise e

        return value

    def get_prep_value(self, value):
        if not value or value == "":
            return ""

        value = self._unicode_dump(value)
        return value

    def value_from_object(self, obj):
        value = getattr(obj, self.attname)
        if not value or value == "":
            return value
        return self._unicode_dump(value)


class CustomDjangoJSONEncoder(DjangoJSONEncoder):
    def default(self, o):
        if isinstance(o, set):
            return list(o)
        else:
            return super().default(o)


class JSONField(OriginalJSONField):
    def __init__(self, *args, **kwargs):
        if not "dump_kwargs" in kwargs:
            kwargs["dump_kwargs"] = {
                "cls": CustomDjangoJSONEncoder,
                "ensure_ascii": False,
                "indent": 2,
            }

        super().__init__(*args, **kwargs)
