from django.forms.utils import ValidationError

try:
    from django.utils.translation import ugettext_lazy as _
except ImportError:
    from django.utils.translation import gettext_lazy as _


from ..serializers import build_serializer

from copy import deepcopy
from codemirror2.widgets import CodeMirrorEditor

from .compat import YAMLField, JSONField


_CODE_MIRROR_OPTION = {
    "options": {
        'lineNumbers': True,
        'tabSize': 4,
        'indentUnit': 2,
        'indentWithTabs': False,
        'theme': "monokai",
        'lineWrapping': True
    },
    "themes": ["monokai"],
    "script_template": "admin/definable_serializer/codemirror_script.html",
}

_CODE_MIRROR_OPTION_FOR_JSON = deepcopy(_CODE_MIRROR_OPTION)
_CODE_MIRROR_OPTION_FOR_YAML = deepcopy(_CODE_MIRROR_OPTION)

_CODE_MIRROR_OPTION_FOR_JSON["options"]["mode"] = "javascript"
_CODE_MIRROR_OPTION_FOR_YAML["options"]["mode"] = "yaml"


__all__ = (
    "AbstractDefinableSerializerField",
    "DefinableSerializerByJSONField",
    "DefinableSerializerByYAMLField",
)


class AbstractDefinableSerializerField:

    def __init__(self, *args, **kwargs):
        self.allow_validate_method = kwargs.pop("allow_validate_method", True)
        self.base_classes = kwargs.pop("base_classes", list())
        super().__init__(*args, **kwargs)

    def clean(self, value, *args, **kwargs):
        try:
            cleaned_data = super().clean(value, *args, **kwargs)
            build_serializer(
                cleaned_data,
                base_classes=self.base_classes,
                allow_validate_method=self.allow_validate_method
            )

        except Exception as except_obj:
            raise ValidationError("Invalid define Format!: {}".format(except_obj))

        return cleaned_data


class DefinableSerializerByJSONField(AbstractDefinableSerializerField, JSONField):
    def formfield(self, **kwargs):
        kwargs["widget"] = CodeMirrorEditor(**_CODE_MIRROR_OPTION_FOR_JSON)
        return super().formfield(**kwargs)


class DefinableSerializerByYAMLField(AbstractDefinableSerializerField, YAMLField):
    def formfield(self, **kwargs):
        kwargs["widget"] = CodeMirrorEditor(**_CODE_MIRROR_OPTION_FOR_YAML)
        return super().formfield(**kwargs)

    # Fix for Django 3.0 and If the Django-YAMLField responds, remove it.
    def from_db_value(self, value, expression, connection, context=None):
        return self.to_python(value)
