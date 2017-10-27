.. `first`:

==============================================================================
restframework-definable-serializerとは
==============================================================================


概要
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

django-restframework(以下restframework)のもつ、モデルからシリアライザーを生成できるモデルシリアライザーはとても強力な機能です。
モデルシリアライザーのおかげでシリアライザー用のコードを書く手間を省くことができます。

しかし入力フィールドの変更は即ちモデルの変更となり、この時点でサーバーへのデプロイ、マイグレーション、テストという一連の作業が確定します。
しかもマイグレーションを伴うメンテナンスは人気のない深夜に行わなければならない場合も多いため、非常に面倒です。

例えばアンケートの質問を扱うモデルがあるとしましょう。
最初は名前、年齢、性別だけを扱うものだったはずが、顧客からの要望で入力フィールドがどんどんと増えていき、最後にはかなりのフィールド数になっていた・・・
こんな経験はなんとしても避けなければなりません。

上記から学べることは **入力フィールドの変更が多く発生するシリアライザーは、シリアライザーの入力フィールドとモデルフィールドを対にしてはいけない** ということです。

モデルフィールドとシリアライザーの入力フィールドが対になっていると、入力項目が変更されるたびにモデルフィールドの変更が発生します。
その時点でデプロイ作業が確定してしまいます。

この問題を解決するには **手軽に変更可能な定義から動的にシリアライザー** を作ることです。

変更可能な定義から作成されたシリアライザーはモデルに束縛されないため、restframeworkが提供する通常のシリアライザーと同様に扱うことができます。

入力データを保存したい場合は、バリデーション後の結果をpickle、またはJSON/YAML化してモデルの単一のフィールドに保存します。

この考え方はSQLのアンチパターンとして扱わがちですが、MySQL, PostgreSQL, SQLite3 それぞれJSONを扱う型を提供しています。
(MariaDBはダイナミックカラムを持ちます。)

これによりエンジニアの手間がかからないシリアライザーを作ることができます。

definable-serializerは、シリアライザーの定義が記述されたYAMLやJSONを読み込み、動的にモデルと対にならないシリアライザーを生成することができます。


------------------------------------------------------------------------------


definable-serializerができること
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

definable-serializerは以下のような機能を備えています。

- YAML/JSON(ファイル, 文字列)からシリアライザーを作成することができます
- admin画面でシリアライザーを定義するための専用のモデルフィールド & 記述されたシリアライザーを確認する機能を提供します
- TemplateHTMLRendererを利用する際に利用可能ないくつかの便利なフィールド(将来的に分離予定)


------------------------------------------------------------------------------


シリアライザー定義の記述例
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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

.. _`yaml-to-serializer`:

YAMLで記述された定義からシリアライザーを作成する
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
実際にYAMLデータからシリアライザーを作成してみましょう。
ここでは名前の入力だけを行うシリアライザーを作成し、データを渡してバリデーションを行います。

djangoシェルを立ち上げて以下のように打ち込んでみましょう。::

    ./manage.py shell


djangoのシェルが立ち上がったら以下のコードを実行してみましょう

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


これはdefinable-serializerが持つ機能の一例に過ぎません。

次はexampleアプリケーションを作成してadmin画面へのインテグレーション及びユーザー側のビューを作成する例を解説します。
