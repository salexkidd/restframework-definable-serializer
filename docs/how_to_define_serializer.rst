.. _`how_to_define_serializer`:

==============================================================================
シリアライザーの定義方法
==============================================================================

restframeworkのシリアライザーは、ユーザーからの入力、そしてサーバーからの出力を適切に処理するために存在します。
これはdjangoのフォームと変わりません。しかし、djangoの提供するフォームはネストた複雑なデータの取り扱いには向いていません。

それに比べ、restframeworkのシリアライザーはネストされたデータもうまく扱うことができるため、djangoのformよりもパワフルです。
djangoのフォームも、formsets等を利用して複数のフォームを並べることもできますが、UI/UXの観点からみると絶望的な状況になるでしょう。

ここではdefinable-serializerを用いて単純な入力だけを持つ単純なシリアライザーと、ネストされたシリアライザーをYAMLで定義する方法を解説します。

またシリアライザーが持つフィールドの記述方法と、バリデートメソッドを含むシリアライザーの記述方法についても解説します。


------------------------------------------------------------------------------


単純なシリアライザーとネストされたシリアライザー
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


単純なシリアライザー
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

単純なシリアライザーとは、フィールド中に別のシリアライザーをネストしていないものを指します。
例えばファーストネームとラストネームのみを扱うような構造のシリアライザーの場合は以下のように記述します。

.. code-block:: yaml

    main:
      name: NameEntry
      fields:
      - name: first_name
        field: CharField
        field_kwargs:
          required: true
          max_length: 100

      - name: last_name
        field: CharField
        field_kwargs:
          required: true
          max_length: 100


この定義をシリアライザークラス化すると以下のようになります。

.. code-block:: python

    NameEntry():
        first_name = CharField(max_length=100, required=True)
        last_name = CharField(max_length=100, required=True)


このシリアライザーに渡せるデータは以下のような形式になります。

.. code-block:: json

    {
        "first_name": "John",
        "last_name": "Smith",
    }



ネストされたシリアライザー
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

ネストされたシリアライザーとは、シリアライザー中に他のシリアライザーをネストしたものを指します。
例えばSNSのようにグループに人を紐付けるような構造のシリアライザーがそれにあたります。

以下の記述例を示します。

.. code-block:: yaml

    main:
      name: Group
      fields:
      - name: group_name
        field: CharField
        field_kwargs:
          label: Group name
          required: true

      - name: persons
        field: Person
        field_kwargs:
          many: true

    depending_serializers:
    - name: Person
      fields:
      - name: first_name
        field: CharField
        field_kwargs:
          required: true

      - name: last_name
        field: CharField
        field_kwargs:
          required: true


この定義をシリアライザークラス化すると以下のようになります。

.. code-block:: python

    Group():
        group_name = CharField(label='Group name', required=True)
        persons = Person(many=True):
            first_name = CharField(required=True)
            last_name = CharField(required=True)


このシリアライザーに渡せるデータは以下のような形式になります(Persons部分がネストされたシリアライザーになります)。

.. code-block:: JSON

    {
        "group_name": "My dearest friends",
        "persons": [
            {"first_name": "John", "last_name": "Smith"},
            {"first_name": "Taro", "last_name": "Yamada"}
        ]
    }


ここで注目するべきは、定義中の ``depending_serializers`` の項目です。
この項目は、mainのシリアライザーを作成する前に予め作成されるシリアライザークラスのリストになります。

``depending_serializers`` 中で先にシリアライザーの定義がされていれば、後に記述されるシリアライザーはそれらを利用することができます。

.. code-block:: yaml

    main:
      name: YourFavorite
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
        field: Animal   # 上で定義されているAnimalを利用しています
        field_kwargs:
          many: true
      - name: foods     # 上で定義されているFoodを利用しています
        field: Food
        field_kwargs:
          many: true

この定義をシリアライザークラス化すると以下のようになります。

.. code-block:: python

    YourFavorite():
        foods_and_animal = FoodsAndAnimals(many=True):
            animals = Animal(many=True):
                name = CharField()
            foods = Food(many=True):
                name = CharField()


------------------------------------------------------------------------------


シリアライザーフィールドの記述方法
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

シリアライザーにはフィールドが必要です。フィールドを記述するにはフィールド名とフィールドタイプを必ず指定します。
任意でフィールドの引数、名前付き引数を指定することができます。以下にフィールドの記述例を示します。


.. code-block:: yaml

    - name: gender          # フィールド名
      field: ChoiceField    # フィールドタイプ(フィールドクラス名)
      field_args:           # フィールドタイプの引数(list)
      - - - male
          - 男性
        - - female
          - 女性
      field_kwargs:         # フィールドタイプの名前付き引数(dict)
        required: true
        label: 性別を入力してください


上記の定義は以下のPythonコードと同義になります。


.. code-block:: python

    >>> from rest_framework import serializers
    >>> gender = serializers.ChoiceField(
    ...     [["male", "男性"], ["female", "女性"]],
    ...     required=True,
    ...     label="性別を入力してください"
    ... )
    >>> gender
    ChoiceField([['male', '男性'], ['female', '女性']], label='性別を入力してください', required=True)


restframeworkが提供するシリアライザーフィールドの利用
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

.. warning::

    definable-serializerでは ``DictField``, ``ListField`` 及び ``SerializerMethodField``
    以外のシリアライザーフィールドが利用可能です。(これらのフィールドは将来的にサポートされる予定です)

definable-serializerではrestframeworkが提供するほとんどのシリアライザーフィールドを利用することができます。
シリアライザーフィールドの一覧については
`restframeworkのシリアライザーフィールドのページを参照してください <http://www.django-rest-framework.org/api-guide/fields/#serializer-fields>`_

restframeworkが提供するシリアライザーフィールドを利用する場合はクラス名だけを指定します。

.. code-block:: python

    - name: my_checkbox    # フィールド名
      field: BooleanField  # フィールドタイプ

    - name: my_char        # フィールド名
      field: CharField     # フィールドタイプ

    - name: my_regex_field # フィールド名
      field: RegexField    # フィールドタイプ
      field_args:
      - a-zA-Z0-9


サードパーティパッケージが提供するシリアライザーフィールドの利用
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

definable-serializerではサードパーティパッケージ、つまりrestframework以外が提供するシリアライザーフィールドも利用可能です。
利用する場合は、各フィールド定義の ``field`` 項目 に ``<パッケージ名>.<モジュール名>.<クラス名>`` の形式で指定することで利用することができます。


.. code-block:: yaml

    main:
      name: AgreementSerailizer
      fields:
      - name: agreement
        field: definable_serializer.extra_fields.CheckRequiredField # サードパッケージが利用するシリアライザーフィールド
        field_kwargs:
          initial: false


この定義をシリアライザークラス化すると以下のようになります。

.. code-block:: python

    IncludeExtraSerializerField():
        agreement = CheckRequiredField()


.. warning::

    definable-serializerでは TemplateHTMLRendererに向けて、いくつかのシリアライザーフィールドを提供しています。
    :ref:`extra_serializer_fields` を御覧ください


------------------------------------------------------------------------------


validateメソッドを含んだシリアライザー
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
シリアライザーやシリアライザーフィールドにはカスタムされたvalidate用のメソッドを必要とする場合があります。
これらはPythonのコードを記述する必要があります。

definable-serializerではフィールド、シリアライザーともにvalidateメソッドを記述することでき来ます。

.. warning::

    シリアライザーの定義中にvalidate_methodを記述できることは便利な半面、危険を伴います。
    例えば、シリアライザーの定義を一般のユーザーに記述させたい要望があったとします。
    もし、一般ユーザーがvalidateメソッド中にシンタックスエラーを含む内容を記述してしまうと、エラーでクラッシュしてしまいます。

    また悪意のあるコードを書かれてしまうと、素直にそれが実行されてしまいます！

    もし、一般ユーザーにシリアライザーを記述させたい場合は、 ``allow_validate_method`` オプションを ``False`` にして
    **validateメソッドの記述を不許可にすることを強く推奨します。** 詳しくは以下を御覧ください。

    - :ref:`definable_serializer_by_yaml_field_class`
    - :ref:`definable_serializer_by_json_field_class`
    - :ref:`utility_functions`


フィールドのvalidateメソッド
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
フィールドにvalidateメソッドを追加するには以下のように記述します。

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


シリアライザーのvalidateメソッド
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

パスワードの確認フィールドのように、他のフィールドの入力データを利用する場合はシリアライザーのvalidateメソッドを記述する必要があります。

そのような必要がある場合は以下のように記述します。

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
