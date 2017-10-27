==============================================================================
その他の有用な情報
==============================================================================


.. _`misc`:


ここではいくつかの有用な情報及び注意点などを記載します。


definable-serializer-exampleについて
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:ref:`example_project` で作成したサンプルプロジェクトになります。
実際に動作するコードを参照したい場合はこちらを御覧ください。

`https://github.com/salexkidd/restframework-definable-serializer-example <https://github.com/salexkidd/restframework-definable-serializer-example>`_


definable-serializerのつかいどころ
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

入力フィールドの変更が多いシリアライザーから、可哀想なモデルを解放するのが
definable-serializerの役割です。

djangoのモデルクラスはデータベースのテーブルをほぼそのまま表現します。
そのような重要なものを簡単に変更するべきではありません。
逆に、フィールドの変更が少ないシリアライザーについてはモデルシリアライザーを用いて
シリアライザーを生成するべきです。

柔軟性はシステムに変更のチャンスを与えます。しかし過ぎたる柔軟性は土台を揺るがし、
システムの崩壊を早めます。

definable-serializerが向いているのは、入力内容が場合によって変更されるものの
一つのモデルクラスで取り扱いたい場合やモデルのメタ情報を扱う場合、
そしてモックでアプリケーションを作る場合です。

それ以外での利用は十分に注意し、考えた末で利用を検討するべきです。


------------------------------------------------------------------------------

.. _`json-field-problem`:

JSONFieldでデータを扱う場合の問題点
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

JSONFieldは有用なモデルフィールドであるものの、いくつかの問題があります。
そのためにdefinable-serializerではいくつかのフィールドを提供しています。

しかし、場合によっては提供しているフィールドを利用できないケースもあります。

特にあなたがpostgreSQLを利用しており、ユーザーからの入力データを検索対象にしたいのならば、
djangoが提供する ``django.contrib.postgres.fields.JSONField`` 利用するのがベストです。
もし、MySQLを利用しているのならば
django-mysql `(http://django-mysql.readthedocs.io/en/latest/model_fields/json_field.html) <http://django-mysql.readthedocs.io/en/latest/model_fields/json_field.html>`_
を利用するとよいでしょう。

ただし、これらのJSONFieldにはJSONEncoderの問題、及び非ASCII文字の問題があります。
もし、definable-serializerが提供する以外のJSONFieldを利用する場合は以下の問題に対処する必要があります。


JSONEncoderの問題
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

PythonでデータをJSONにシリアライズする場合、実は大きな落とし穴があります。
それは、ネイティブデータ型である ``set型`` がpythonに付属するJSONエンコードすることができない問題です。

以下のコードを実行すると、TypeErrorが発生するのを確認できます。

.. code-block:: python

    >>> import json
    >>> json.dumps(set([1,2,3]))
    TypeError: Object of type 'set' is not JSON serializable


困ったことに、restframeworkが提供するMultipleChoiceフィールドはバリデーション後の結果を
``set型`` で返すため、そのままJSONFieldに値を渡すとエラーが発生してしまいます。

この問題を解決するには ``DjangoJSONEncoder`` を継承し、``set型`` のデータを ``list型`` に変換するように変更します。


.. code-block:: python

    from django.db import models
    from django.core.serializers.json import DjangoJSONEncoder
    from django.contrib.postgres.fields import JSONField


    class MyCustomJSONEncoder(DjangoJSONEncoder):
        def default(self, o):
            if isinstance(o, set):
                return list(o)
            else:
                return super().default(o)


    class TestModel(models.Model):
        answer = JSONField(encoder=MyCustomJSONEncoder)


これでTypeErrorが起きることなくユーザーからの入力を保存することができます。


非ASCII文字列の問題
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

JSONでデータを取り扱うにはもうひとつの問題があります。それは非ASCII文字の取り扱いです。
以下のデータを見てみましょう。

.. code-block:: json

    {"favorite_food": "\ud83c\udf54"}


これは、ハンバーガーのEmoji(🍔)です。しかし、'\\ud83c\\udf54'は我々の目には全く美味しそうに見えません。

目に見る必要がないデータならばこれで問題ありません。しかし、admin画面で入力値を確認しようとして、
'\\ud83c\\udf54' のような文字列が表示されたらどうでしょうか。

エンジニアならばこの文字列をエンコードして意味を知ることができるかもしれません。しかし、データを実際に扱う
オペレーターから見ると不吉な何かにしか見えないでしょう。

.. figure:: imgs/bad_taste_burger.png

    ハンバーガー的な何か

この問題を避けるには、``eusure_ascii`` オプションを ``False`` にしてdumpを行う必要があります。
以下にコード例を示します。

.. code-block:: python

    >>> import json
    >>> input_data = {
    ...     "favorite_food": "🍔"
    ... }
    >>> json.dumps(input_data)
    '{"favorite_food": "\\ud83c\\udf54"}'
    >>> json.dumps(input_data, ensure_ascii=False)
    '{"favorite_food": "🍔"}'
