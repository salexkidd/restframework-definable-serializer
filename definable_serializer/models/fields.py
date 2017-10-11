from django.forms.utils import ValidationError
from django.utils.translation import ugettext_lazy as _

from ..serializers import build_serializer

from copy import deepcopy
from codemirror2.widgets import CodeMirrorEditor
from jsonfield.fields import JSONField
# from yamlfield.fields import YAMLField
from .compat import YAMLField

import simplejson

_CODE_MIRROR_OPTION = {
    "options": {
        'mode': 'yaml',
        'lineNumbers': True,
        'tabSize': 2,
        'indentUnit': 2,
        'indentWithTabs': False,
        'theme': "monokai",
    },
    "modes": ['yaml'],
    "themes": ["monokai"],
    "script_template": "admin/definable_serializer/codemirror_script.html",
}

_CODE_MIRROR_OPTION_FOR_YAML = deepcopy(_CODE_MIRROR_OPTION)
_CODE_MIRROR_OPTION_FOR_JSON = deepcopy(_CODE_MIRROR_OPTION)

_CODE_MIRROR_OPTION_FOR_YAML["modes"] = ["yaml"]
_CODE_MIRROR_OPTION_FOR_JSON["modes"] = ["json"]

__all__ = (
    "DefinableSerializerByJSONField",
    "DefinableSerializerByYAMLField",
)


class AbstractDefinableSerializerField:
    def clean(self, value, *args, **kwargs):
        try:
            value = super().clean(value, *args, **kwargs)
            build_serializer(value)

        except Exception as except_obj:
            raise ValidationError("Invalid Format!: {}".format(except_obj))

        return value


class DefinableSerializerByJSONField(AbstractDefinableSerializerField, JSONField):
    def formfield(self, **kwargs):
        kwargs["widget"] = CodeMirrorEditor(**_CODE_MIRROR_OPTION_FOR_JSON)
        return super().formfield(**kwargs)


class DefinableSerializerByYAMLField(AbstractDefinableSerializerField, YAMLField):
    def formfield(self, **kwargs):
        kwargs["widget"] = CodeMirrorEditor(**_CODE_MIRROR_OPTION_FOR_YAML)
        return super().formfield(**kwargs)
