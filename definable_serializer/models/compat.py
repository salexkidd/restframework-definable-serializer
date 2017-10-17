import six
import ruamel.yaml as ruamel_yaml
from django.core.exceptions import ValidationError

from yamlfield.fields import YAMLField as OriginalYAMLField


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
