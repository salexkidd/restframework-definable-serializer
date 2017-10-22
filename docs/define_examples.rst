========================
シリアライザーの定義例
========================

.. _`define_examples`:


単一のシリアライザー
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
単一のシリアライザーとは、フィールド中に別のシリアライザーを利用していないものを指します。

.. code-block:: yaml

    main:
      name: Unit
      fields:
      - name: favorite_food
        field: CharField
        field_kwargs:
          required: true
          max_length: 100


上の定義をシリアライザー化すると以下のようになります。

.. code-block:: python

    Single():
        favorite_food = CharField(max_length=100, required=True)

単一のシリアライザーを定義する場合は ``main`` に以下の項目を定義する必要があります。

* シリアライザー名(キャメルケース)
* 提供するフィールド
    * フィールド名(スネークケース)
    * フィールドタイプ
    * フィールドの引数および名前付き引数


------------------------------------------------------------------------------


複雑なシリアライザー
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
複雑なシリアライザーとは、シリアライザー中に他のシリアライザーを利用しているものを指します。
例えば、SNSのようにグループに人を紐付けるシリアライザーを用意する場合、以下のように定義します。

.. code-block:: yaml

    main:
      name: Group
      fields:
      - name: group_name
        field: CharField
        field_kwargs:
          label: Group name
          required: true
      - name: person_list
        field: PersonSerializer
        field_kwargs:
          many: true

    depending_serializers:
    - name: Person
      fields:
      - name: username_field
        field: CharField
        field_kwargs:
          required: true
      - name: email_field
        field: EmailField
        field_kwargs:
          required: true


上の定義をシリアライザー化すると以下のようになります。

.. code-block:: python

    Group():
        group_name = CharField(label='Group name', required=True)
        person_list = Person(many=True):
            username_field = CharField(initial='', label='Username', required=True)
            email_field = EmailField(initial='', label='Email', required=True)

ここで注目するべきは ``depending_serializers`` の項目です。
この項目は、mainのシリアライザーを作成する前に予め作成されるシリアライザーの一覧になります。


.. hint::
    depending_serializers中でも先に定義さえされていれば、
    後にdepending_serializers中に記述されるシリアライザーは、その定義を利用することができます。

    .. code-block:: yaml

        main:
          name: Main
          fields:
          - name: foods_and_animal
            field: FoodsAndAnimals
            field_kwargs:
              many: true

        depending_serializers:
        - name: Animal
          fields:
          - name: name
            field: CharField
        - name: Food
          fields:
          - name: name
            field: CharField
        - name: FoodsAndAnimals
          fields:
          - name: animals
            field: Animal
            field_kwargs:
              many: true
          - name: foods
            field: Food
            field_kwargs:
              many: true

    以上の定義は以下のシリアライザーとして扱われます。

    .. code-block:: python

        Main():
            foods_and_animal = FoodsAndAnimals(many=True):
                animals = Animal(many=True):
                    name = CharField()
                foods = Food(many=True):
                    name = CharField()


------------------------------------------------------------------------------


restframework以外が提供するシリアライザーフィールドの利用
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
definable-serializerではrestframework以外が提供するフィールドも利用可能です。

各フィールド定義中の ``field`` に ``<パッケージ名>.<モジュール名>.<クラス名>`` の形式で
指定することで利用することができます。


.. code-block:: yaml

    main:
      name: IncludeExtraSerializerField
      fields:
      - name: foods_and_animal
        field: definable_serializer.extra_fields.CheckRequiredField
        field_kwargs:
          many: true


上の定義をシリアライザー化すると以下のようになります。

.. code-block:: python

    IncludeExtraSerializerField():
        agreement = CheckRequiredField()


------------------------------------------------------------------------------


バリデートメソッドを含んだシリアライザー
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
シリアライザー及びフィールドにはカスタムされたバリデートメソッドを必要とする場合があります。
この場合はpythonのコードを記述する必要があります。definable-serializerでは以下のフィールド、シリアライザー全体の
バリデートメソッドともに定義の中にコードを記述することで実現可能です。


フィールドのバリデートメソッド
++++++++++++++++++++++++++++++++++++++++
フィールドにバリデートメソッドを追加するには以下のように記述します。

.. code-block:: yaml

    main:
      name: FieldValidationTestSerializer
      fields:
        - name: test_field_one
          field: CharField
          field_kwargs:
            required: true

          # Field validation method
          validate_method: |
            def validate_method(self, value):
                from rest_framework import serializers
                if value != "correct_data":
                    raise serializers.ValidationError("Please input 'correct_data'")
                return value


以下にバリデーションの結果を示します。


.. code-block:: python

    >>> from definable_serializer.serializers import build_serializer_by_yaml
    >>> YAML_DEFINE_DATA = """<< FieldValidationTestSerializer YAML DATA >>"""
    >>> serializer_class = build_serializer_by_yaml(YAML_DEFINE_DATA)
    >>> serializer = serializer_class(data={"test_field_one": "test"})

    # フィールドバリデーションエラー例
    >>> serializer.is_valid()
    False
    >>> serializer.errors
    ReturnDict([('test_field_one', ["Please input 'correct_data'"])])

    # フィールドバリデーション成功例
    >>> serializer = serializer_class(data={"test_field_one": "correct_data"})
    >>> serializer.is_valid()
    True


シリアライザーのバリデートメソッド
++++++++++++++++++++++++++++++++++++++++
パスワードの確認フィールドのように、他のフィールドの入力データを利用する場合はシリアライザーの
バリデートメソッドを記述する必要があります。

.. code-block:: yaml

    main:
      name: PasswordTestSerializer
      fields:
      - name: password
        field: CharField
        field_kwargs:
          required: true
      - name: password_confirm
        field: CharField
        field_kwargs:
          required: true

      # Serializer  validation method
      serializer_validate_method: |-
        def validate_method(self, data):
            from rest_framework import serializers

            if data["password"] != data["password_confirm"]:
                raise serializers.ValidationError({
                    "password_confirm": "The two password fields didn't match.'."
                })
            return data


以下にバリデーションの結果を示します。


.. code-block:: python

    >>> from definable_serializer.serializers import build_serializer_by_yaml
    >>> YAML_DEFINE_DATA = """<< PasswordTestSerializer YAML DATA >>"""
    >>> serializer_class = build_serializer_by_yaml(YAML_DEFINE_DATA)

    # バリデーションエラー例
    >>> serializer = serializer_class(
    ...    data={"password": "new_password", "password_confirm": "foobar"})
    ...
    >>> serializer.is_valid()
    False

    >>> serializer.errors
    ReturnDict([('password_confirm',
                 ["The two password fields didn't match."])])

    # バリデーション成功例
    >>> serializer = serializer_class(
    ...     data={"password": "new_password", "password_confirm": "new_password"})
    ...
    >>> serializer.is_valid()
    True
