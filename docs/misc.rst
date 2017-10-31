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


------------------------------------------------------------------------------


definable-serializerのつかいどころ
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

入力フィールドの変更が多いシリアライザーから可哀想なモデルを解放するのがdefinable-serializerの役割です。
逆に、フィールドの変更が少ないシリアライザーについてはモデルシリアライザーを用いてシリアライザーを生成するべきです。

柔軟性はシステムに変更のチャンスを与えますが、過ぎたる柔軟性は土台を揺るがしシステムの崩壊時期を早めます。

definable-serializerが向いているのは、入力内容が場合によって変更されるものの1つのモデルクラスで取り扱いたい場合や、モデルのメタ情報を扱う場合、そしてモックを作る場合です。

それ以外での利用は十分に注意し、考えた末で利用を検討するべきです。


------------------------------------------------------------------------------


.. _`json-field-problem`:

JSONFieldでデータを扱う場合の問題点
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

サードパッケージ、及びdjangoが提供するJSONFieldは有用なモデルフィールドであるものの、利用するには2つの問題があります。

1つはJSONEncoderの問題、もうひとつが非ASCII文字列の問題です。

そのためにdefinable-serializerではいくつかのフィールドを提供しています(詳しくは :ref:`model_fields` を参照してください)。

しかし、場合によっては提供しているフィールドを利用できないケースもあります。

特に、postgreSQLを利用しており、ユーザーからの入力データを検索対象にしたいのならば、djangoが提供する
``django.contrib.postgres.fields.JSONField`` 利用するのがベストです。

もし、MySQLを利用しているのならば `django-mysql <http://django-mysql.readthedocs.io/en/latest/model_fields/json_field.html>`_
を利用するとよいでしょう。

ただし、これらのJSONFieldにはJSONEncoder、及び非ASCII文字に関する問題があります。

もし、definable-serializerが提供する以外のJSONFieldを利用するにはこれらの問題に対処する必要があります。


.. _`jsonencoder_problem`:

JSONEncoder問題
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

PythonでデータをJSONにシリアライズする場合、大きな落とし穴があります。
それは、ネイティブデータ型である ``set型`` がpythonに付属するjsonモジュールではエンコードすることができないからです。

``set型`` を含むデータをjson化すると`` TypeError`` が発生するのを確認できます。

.. code-block:: python

    >>> import json
    >>> json.dumps(set([1,2,3]))
    TypeError: Object of type 'set' is not JSON serializable


困ったことに、restframeworkが提供するMultipleChoiceフィールドはバリデーション後の結果を
``set型`` で返すため、そのままJSONFieldに値を渡すとエラーが発生してしまいます。

この問題を解決するには ``DjangoJSONEncoder`` を継承して自作のEncoderクラス用意し、 ``set型`` のデータを ``list型`` に変換するように変更します。


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


.. _`ensure_ascii_problem`:

非ASCII文字列問題
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

以下のJSON文字列を見てみましょう

.. code-block:: json

    {"favorite_food": "\ud83c\udf54"}


これは、ハンバーガー(🍔)のEmojiです。しかし、'\\ud83c\\udf54' は全く美味しそうに見えません。
目に見る必要がないデータならばこれで問題ありませんが、adminサイトで入力されたデータを確認しようとして、"\\ud83c\\udf54" のような文字列が表示されたらどうでしょうか。

エンジニアならばこの文字列をデコードして意味を知ることができるかもしれません。
しかし、実際にデータを扱うオペレーターから見ると不吉な何かにしか見えないでしょう。

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


``ensure_ascii`` を ``False`` にしたい場合、モデルフィールドのソースコードを読み、各自で　``json.dumps`` の部分を変更してオプションを渡すようにしなければなりません。


JSONFieldの供給過多問題
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

JSONFieldにはもう1つ問題があります。世界中のエンジニアはJSONを好んで利用します。
その結果、Googleで調べるといくつものJSONFieldがdjangoに提供されていることが確認できます。

* `https://pypi.python.org/pypi/jsonfield <https://pypi.python.org/pypi/jsonfield>`_
* `https://pypi.python.org/pypi/django-jsonfield <https://pypi.python.org/pypi/django-jsonfield>`_
* `https://pypi.python.org/pypi/django-json-field <https://pypi.python.org/pypi/django-json-field>`_
* `http://django-mysql.readthedocs.io/en/latest/model_fields/json_field.html <http://django-mysql.readthedocs.io/en/latest/model_fields/json_field.html>`_

また、djangoも ``django.contrib.postgres.fields.JSONField`` を提供しています。

ハッキリ言えば供給が多すぎて、どれを利用してよいか迷ってしまいます。

きっと優秀なあなたならば間違えないでしょう。しかし、筆者はpipでインストールを行う際に十中八九間違えます。
(余談ながら、上記パッケージの大半が :ref:`jsonencoder_problem` 及び :ref:`ensure_ascii_problem` を抱えています。)

これらの問題に一番対処しやすいのが `django-jsonfield <https://pypi.python.org/pypi/django-jsonfield>`_ (上記リストの先頭)です。

フィールドの引数に対して ```dump_kwargs`` を渡すことで、JSONEncoder及びensucre_ascii問題に対処することができます。

definable-serializerでは、 :ref:`definable_serializer_by_json_field_class` および :ref:`compat_json_field`
においてdjango-jsonfieldを利用しています。


------------------------------------------------------------------------------


各種配布先
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    git
        `https://github.com/salexkidd/restframework-definable-serializer <https://github.com/salexkidd/restframework-definable-serializer>`_
        `https://github.com/salexkidd/restframework-definable-serializer-example <https://github.com/salexkidd/restframework-definable-serializer-example>`_

    pypi
        `https://pypi.org/project/restframework-definable-serializer/ <https://pypi.org/project/restframework-definable-serializer/>`_
        `https://pypi.python.org/pypi/restframework-definable-serializer/0.1.8 <https://pypi.python.org/pypi/restframework-definable-serializer/0.1.8>`_


------------------------------------------------------------------------------

Todo
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

TodoはGithub上で管理しています。


------------------------------------------------------------------------------

連絡先
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    twitter: `@salexkidd <https://twitter.com/salexkidd>`_


------------------------------------------------------------------------------

ライセンス
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Copyright 2017 salexkidd

    Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
