import io

import ruamel.yaml as ruamel_yaml
import six
from django.core.exceptions import ValidationError
from django.core.serializers.json import DjangoJSONEncoder
from jsonfield.fields import JSONField as OriginalJSONField
from yamlfield.fields import YAMLField as OriginalYAMLField


class YAMLField(OriginalYAMLField):

    def _unicode_dump(self, value):
        yaml = ruamel_yaml.YAML(typ='rt', pure=True)
        buf = io.StringIO()
        yaml.dump(value, buf)
        return buf.getvalue()

    def to_python(self, value):
        if value == "":
            return None
        try:
            if isinstance(value, six.string_types):
                yaml = ruamel_yaml.YAML(typ='rt')
                return yaml.load(value)
        except Exception as e:
            raise e

        return value

    def get_prep_value(self, value):
        if not value or value == "":
            return ""

        return self._unicode_dump(value)

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
