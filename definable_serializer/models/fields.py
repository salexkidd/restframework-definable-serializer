"""
Copyright 2017 salexkidd

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

from django.forms.utils import ValidationError
from django.utils.translation import ugettext_lazy as _

from ..serializers import build_serializer

from copy import deepcopy
from codemirror2.widgets import CodeMirrorEditor
# from jsonfield.fields import JSONField


from .compat import YAMLField, JSONField


_CODE_MIRROR_OPTION = {
    "options": {
        'lineNumbers': True,
        'tabSize': 2,
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
        super().__init__(*args, **kwargs)

    def clean(self, value, *args, **kwargs):
        try:
            cleaned_data = super().clean(value, *args, **kwargs)
            build_serializer(cleaned_data, self.allow_validate_method)

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
