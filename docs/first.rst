==============================================================================
はじめに
==============================================================================

.. _`first`:

restframework-definable-serializerとは
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

django-restframework(以下restframework)のもつ、モデルからシリアライザーを生成できる
*モデルシリアライザー* はとても強力な機能です。
ユーザーからの入力を受け付けるシリアライザーをモデルから生成することができるため、大幅に手間を省くことができます。

しかし入力フィールドの変更は即ちモデルの変更となり、この時点でサーバーへのデプロイ、マイグレーション、テストという
一連の作業を行わなければならないことが確定されます。大抵の場合、マイグレーションを伴うメンテナンスは
人気のない深夜に作業を行わなければならないため、非常に面倒です。

例えば、アンケートを扱うモデルがあるとしましょう。
最初は名前、年齢、性別の3つを扱うものだったはずが、
顧客からの要望で入力フィールドがどんどんと増えていき、最後にはかなりのフィールド数になっていた・・
読んでいらっしゃる方の中には同様の経験をしたことがある人もいるのではないでしょうか。

この経験から学べることは、
**入力フィールドの変更が多く発生するようなシリアライザーを作る場合は、
シリアライザーの入力フィールドとモデルのフィールドを対にしてはいけない** ということです。

モデルのフィールドとシリアライザーの入力フィールドが対になっているということは、入力項目が変更されるたびに
モデルフィールドの変更が発生します。その時点でデプロイ作業が確定してしまいます。

この問題を解決するには **手軽に変更可能なデータから動的にシリアライザー** を作ることです。

作成されたシリアライザーはモデルに束縛されないため、restframeworkが提供するノーマルのシリアライザー
(rest_framework.serializers.Serializer)と同様に扱うことが出来ます。
入力データを保存したい場合は、バリデーション後の結果をpickle、YAML化してモデルの単一のフィールドに保存します。

これによりデプロイのいらない容易変更可能なモデルフィールドと対にならずに扱えるシリアライザーを作ることができます。

restframework-definable-serializer(以下definable-serializer)は、シリアライザーの定義が記述された
YAMLやJSONを読み込み、動的にモデルと対にならないシリアライザーを生成することが出来ます。

また、以下definable-serializerは以下のような機能を提供しています。

- YAML/JSON ファイルやデータからシリアライザーを作成する機能
- admin画面でシリアライザーを定義する専用のモデルフィールド & 定義されたシリアライザーを確認する機能
- TemplateHTMLRendererを利用する際に利用可能ないくつかの便利なフィールド(将来的に分離予定)


------------------------------------------------------------------------------


シリアライザー定義の記述例
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

以下にYAMLで定義した簡単なシリアライザーの例を紹介します。


.. code-block:: yaml

    main:
      name: EnqueteSerializer
      fields:
      - name: name
        field: CharField
        field_kwargs:
          required: true
          max_length: 100
      - name: age
        field: IntegerField
        field_kwargs:
          required: true
      - name: gender
        field: ChoiceField
        field_args:
        - - - male
            - 男性
          - - female
            - 女性
        field_kwargs:
          required: true


上の定義は名前、年齢、性別の3つの入力を持つシリアライザーの例です。
この定義をdefinable-serializerを用いてシリアライザー化すると以下のようになります。

.. code-block:: python

    EnqueteSerializer():
        name = CharField(max_length=100, required=True)
        age = IntegerField(required=True)
        gender = ChoiceField([['male', '男性'], ['female', '女性']], required=True)


これをrestframeworkの持つBrowsableAPIRendererで表示すると以下の様になります。


.. figure:: imgs/browse_enquete_serializer.png

    BrowsableAPIRendererで表示した例


------------------------------------------------------------------------------


YAML定義からシリアライザーを作成する
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
実際にYAMLデータからシリアライザーを作成してみましょう。
ここでは名前の入力だけを行うシリアライザーを作成し、データを渡してバリデーションを行います。

djangoシェルを立ち上げて以下のように打ち込んでみましょう。


.. code-block:: python

    >>> from definable_serializer.serializers import build_serializer_by_yaml

    # 名前だけを扱うシリアライザーのYAML定義
    >>> YAML_DEFINE_DATA = """
    ... main:
    ...   name: YourFirstSerializer
    ...   fields:
    ...   - name: name
    ...     field: CharField
    ...     field_kwargs:
    ...       required: true
    ...       max_length: 100
    ... """

    # シリアライザー化
    >>> serializer_class = build_serializer_by_yaml(YAML_DEFINE_DATA)
    >>> serializer_class()
    FirstSerializer():
        name = CharField(max_length=100, required=True)

    # バリデーション成功例
    >>> serializer = serializer_class(data={"name": "Taro Yamada"})
    >>> serializer.is_valid()
    >>> serializer.validated_data
    OrderedDict([('name', 'Taro Yamada')])

    # バリデーションエラー例(空の場合)
    >>> serializer = serializer_class(data={"name": ""})
    >>> serializer.is_valid()
    False
    >>> serializer.errors
    {'name': ['This field may not be blank.']}

    # バリデーションエラー例(100文字を超えていた場合 )
    >>> serializer = serializer_class(data={"name": "a" * 101})
    >>> serializer.is_valid()
    False
    >>> serializer.errors
    {'name': ['Ensure this field has no more than 100 characters.']}
