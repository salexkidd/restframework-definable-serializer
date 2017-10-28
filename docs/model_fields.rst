==============================================================================
提供するモデルフィールドクラス
==============================================================================


.. _`compat_model_fields`:


definable-serializerではシリアライザーを記述するためのフィールドと、
ユーザーからの入力データを保存するためのフィールドを提供しています。


シリアライザーの定義を保存するモデルフィールド
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

definable-serializerでは、JSON及びYAMLで記述された文字列及びファイルからシリアライザーを作ることができます。
特にadmin画面でシリアライザーを記述することで、デプロイの手間を緩和するのが目的です。
admin画面でテキストデータの編集を行うのは難しい話ではないものの、YAMLやJSON定義をハイライト無しで記述するのはちょっとした苦行です。

この問題を解決するために、CodeMirror2ウィジェットを利用してハイライトサポートを行う
2つのシリアライザー定義用のフィールドを用意しています。


DefinableSerializerByYAMLField
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

DefinableSerializerByYAMLFieldはdjango-yamlfield
`(https://github.com/datadesk/django-yamlfield) <https://github.com/datadesk/django-yamlfield>`_ が
提供するYAMLFieldをラップし、CodeMirror2ウィジェット及び非ASCII文字が正しく表示することができます。

以下に使用例を示します。


.. code-block:: python

    class Survey(models.Model):
        ..

        question = DefinableSerializerByYAMLField()

.. figure:: imgs/codemirror2_with_yaml.png


DefinableSerializerByJSONField
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

DefinableSerializerByJSONFieldは
jsonfield `(https://github.com/dmkoch/django-jsonfield) <https://github.com/dmkoch/django-jsonfield>`_ が
提供するJSONFieldをラップし、CodeMirror2ウィジェット及び非ASCII文字が正しく表示することができます。

以下に使用例を示します。


.. code-block:: python

    class Survey(models.Model):
        ..

        question = DefinableSerializerByJSONField()

.. figure:: imgs/codemirror2_with_json.png


------------------------------------------------------------------------------


.. _`methods-of-storing-input-data`:

ユーザーからの入力データを保存するモデルフィールド
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. (あとで利用する)
.. :ref:`storing-input-data` でも取り上げたように、モデルに結びつかないシリアライザーにユーザーから
.. 渡されてバリデーションが完了したデータを永続的に保存するには、保存情報を扱うモデルの単一のフィールドに
.. シリアライズ(直列化)された状態でデータを保存します。
..
.. ようはPythonのネイティブなデータを何らかの形に変換してつまりデータベースのカラムにさえ保存できれば
.. どんな形でも構いません。データのシリアライズによく用いられるのが JSON, YAML, Pickle, Base64です。
..
.. 各種それぞれモデルフィールドとしてサードパーティパッケージとしてモデルフィールドが提供されています。
..
.. * django-base64field `(https://pypi.python.org/pypi/django-base64field) <https://pypi.python.org/pypi/django-base64field>`_
.. * django-yamlfield `(https://github.com/datadesk/django-yamlfield) <https://github.com/datadesk/django-yamlfield>`_
.. * django-picklefield `(https://github.com/shrubberysoft/django-picklefield) <https://github.com/shrubberysoft/django-picklefield>`_
..
.. その中でももっとも人気のある方法がJSONによるシリアライズです。
..
.. JSONFieldを提供するパッケージを紹介します。
..
.. * jsonfield `(https://github.com/dmkoch/django-jsonfield) <https://github.com/dmkoch/django-jsonfield>`_
.. * django-mysql `(http://django-mysql.readthedocs.io/en/latest/model_fields/json_field.html) <http://django-mysql.readthedocs.io/en/latest/model_fields/json_field.html>`_
..
.. そしてdjangoは標準で ``django.contrib.postgres.fields.JSONField`` を提供しており、これを利用すれば
.. `保存したJSONFieldを検索の対象として利用することができます。 <https://docs.djangoproject.com/en/1.11/ref/contrib/postgres/fields/#querying-jsonfield>`_
.. それは `django-mysqlのJSONField <http://django-mysql.readthedocs.io/en/latest/model_fields/json_field.html#querying-jsonfield>`_ でも同様です。
..
.. しかし、JSONField、YAMLFieldともにいくつかの問題があります。
..
.. ここではそれぞれのフィールドが抱える問題点と、definable_serializerが提供するこれらのフィールドをラップした
.. 問題を修正するためのモデルフィールドを紹介します。


:ref:`storing-input-data` でも取り上げたように、モデルに結びつかないシリアライザーにユーザーから
渡されてバリデーションが完了したデータを永続的に保存するには、保存情報を扱うモデルの単一のフィールドに
シリアライズ(直列化)された状態でデータを保存します。

ようはPythonのネイティブなデータをテキストやバイナリに変換してデータベースのカラムにさえ保存できれば
どんな形でも構いません。データのシリアライズによく用いられるのが JSON, YAMLです。

definable-serializerではユーザーからの入力を保存するために2つのモデルフィールドを用意しています。


JSONField
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

JSONは非常に人気の高いシリアライズの形式です。

しかし、Pythonに付随するJSONEncoderにはPythonのネイティブなデータである ``set型`` を
シリアライズすることができません。

また正しく設定を行わないと非ASCII文字を"\\uXXXX"で表すため、入力情報を確認すると見苦しい状態になります。

definable-serializerでは、 `jsonfield <https://github.com/dmkoch/django-jsonfield>`_
が提供するJSONFieldをラップし、この2つの問題を解消するコンパチビリティクラスを用意しています。

以下に使用例を示します。


.. code-block:: python

    from definable_serializer.models.compat import JSONField as CompatJSONField

    class Answer(models.Model):

        ..

        answer = CompatJSONField(
            verbose_name="answer data",
            help_text="answer data"
        )


このモデルフィールドを使うとadmin画面で以下のように表示されます。


.. figure:: imgs/compat_json_field.png

    Emoji(🍔)も正しく表示されます


YAMLField
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

YAMLはJSONと同様、テキストでデータシリアライズします。記号が少なくインデントでデータ構造を表すため、
Pythonのコードのように美しく、可読性に優れます。

definable-serializerでは、 django-yamlfield `(https://github.com/datadesk/django-yamlfield) <https://github.com/datadesk/django-yamlfield>`_
が提供するYAMLFieldをラップし、非ASCII文字が正しく表示されるコンパチビリティクラスを用意しています。

以下に使用例を示します。


.. code-block:: python

    from definable_serializer.models.compat import YAMLField as CompatYAMLField

    class Answer(models.Model):

        ..

        answer = CompatYAMLField(
            verbose_name="answer data",
            help_text="answer data"
        )

.. figure:: imgs/compat_yaml_field.png
    :scale: 40

    絵文字も正しく表示されます
