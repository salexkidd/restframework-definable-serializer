.. _`utility_functions`:

==============================================================================
提供する関数
==============================================================================

definable-serializerでは、YAMLやJSONで記述された定義からシリアライザーを作成する5つの関数を提供しています。

- build_serializer
- build_serializer_by_json
- build_serializer_by_json_file
- build_serializer_by_yaml
- build_serializer_by_yaml_file


build_serializer関数
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. function:: build_serializer(definition, allow_validate_method=True)

``build_serializer`` は定義が記述されたPythonのDictからシリアライザークラスを作成します。

``allow_validate_method`` が ``False`` の場合、シリアライザーの定義中に ``validate_method`` が記述されていると ``ValidationError`` が発生します。

.. code-block:: python

    >>> from definable_serializer.serializers import build_serializer
    >>> serializer_definition = {
    ...     "main": {
    ...         "name": "TestSerializer",
    ...         "fields": [
    ...             {
    ...                 "name": "test_field",
    ...                 "field": "CharField",
    ...                 "field_kwargs": {
    ...                     "max_length": 100,
    ...                 }
    ...             }
    ...         ],
    ...         "validate_method": """def validate_method(self, value):
    ...             return value
    ...         """
    ...     },
    ... }
    # allow_validate_methodがTrueの場合
    >>> serializer_class = build_serializer(serializer_definition, allow_validate_method=True)
    >>> serializer_class()
    TestSerializer():
        test_field = CharField(max_length=100)

    # allow_validate_methodがFalseの場合
    >>> serializer_class = build_serializer(serializer_definition, allow_validate_method=False)
    ValidationError: ['serializer validate_method not allowed.']


------------------------------------------------------------------------------


.. _`build_serializer_by_json_function`:

build_serializer_by_json関数
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. function:: build_serializer_by_json(definition, allow_validate_method=True)

``build_serializer_by_json`` は定義が記述されたJSON文字列からシリアライザークラスを作成します。

``allow_validate_method`` が ``False`` の場合、シリアライザーの定義中に ``validate_method`` が記述されていると ``ValidationError`` が発生します。

.. code-block:: python

    >>> from definable_serializer.serializers import build_serializer_by_json
    >>> json_str = """
    ... {
    ...     "main": {
    ...         "name": "TestSerializer",
    ...         "fields": [
    ...             {
    ...                 "name": "test_field",
    ...                 "field": "CharField",
    ...                 "field_kwargs": {"max_length": 100}
    ...             }
    ...         ],
    ...         "validate_method": "def validate_method(self, value):\\n            return value\\n        "
    ...     }
    ... }
    ... """

    # allow_validate_methodがTrueの場合
    >>> serializer_class = build_serializer_by_json(json_str, allow_validate_method=True)
    >>> serializer_class()
    TestSerializer():
        test_field = CharField(max_length=100)

    # allow_validate_methodがFalseの場合
    >>> serializer_class = build_serializer_by_json(json_str, allow_validate_method=False)
    ValidationError: ['serializer validate_method not allowed.']


------------------------------------------------------------------------------


build_serializer_by_json_file関数
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. function:: build_serializer_by_json_file(json_filepath, allow_validate_method=True)

``build_serializer_by_json_file`` は定義が記載されたJSONファイルからシリアライザークラスを作成します。


この関数の動作はファイルパスを受け取る以外、 ``build_serializer_by_json`` 関数と同等です。


------------------------------------------------------------------------------


.. _`build_serializer_by_yaml_function`:

build_serializer_by_yaml関数
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. function:: build_serializer_by_yaml(definition, allow_validate_method=True)

``build_serializer_by_json`` 定義が記述されたYAML文字列からシリアライザークラスを作成します。

``allow_validate_method`` が ``False`` の場合、シリアライザーの定義中に ``validate_method`` が記述されていると ValidationErrorが発生します。

.. code-block:: python

    >>> from definable_serializer.serializers import build_serializer_by_yaml
    >>> yaml_str = """
    ... main:
    ...   name: "TestSerializer"
    ...   fields:
    ...   - name: test_field
    ...     field: CharField
    ...     field_kwargs:
    ...       max_length: 100
    ...   validate_method: |
    ...   def validate_method(self, value):
    ...       return value
    ... """

    # allow_validate_methodがTrueの場合
    >>> serializer_class = build_serializer_by_yaml(yaml_str, allow_validate_method=True)
    >>> serializer_class()
    TestSerializer():
        test_field = CharField(max_length=100)

    # allow_validate_methodがFalseの場合
    >>> serializer_class = build_serializer_by_yaml(yaml_str, allow_validate_method=False)
    ValidationError: ['serializer validate_method not allowed.']


------------------------------------------------------------------------------


build_serializer_by_yaml_file関数
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. function:: build_serializer_by_yaml_file(yaml_filepath, allow_validate_method=True)

``build_serializer_by_yaml_file`` 定義が記載されたYAMLファイルからシリアライザークラスを作成します。


この関数の動作はファイルパスを受け取る以外、 ``build_serializer_by_yaml`` 関数と同等です。
