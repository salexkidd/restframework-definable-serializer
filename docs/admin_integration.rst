=======================================
admin画面からシリアライザーを定義する
=======================================

*はじめに* でも書いたように、definable-serializerの一番の目的はデプロイ作業を行わない、それは即ち
**エンジニアが苦労しないため** に作られたものです。故にシリアライザーの定義をファイルに書いては
意味がありません。

その問題を解決する一番の方法はWebインターフェイスです。

そして、運の良いことに我々はrestframeworkを利用している時点でdjangoを利用しており、
djangoにははじめからadmin画面が用意されています！

definable-serializerでは既存のモデルにも簡単にYAML/JSONでシリアライザーを定義するための
``DefinableSerializerByYAMLField`` と ``DefinableSerializerByJSONField``
という2つのモデルフィールドを用意しています。

さらにadmin画面中でシリアライザーの定義を確認するための機能を提供する ``DefinableSerializerAdmin`` クラスを提供しています。

ここでは簡単なプロジェクトを作成し、組込例を紹介します。


アンケート用プロジェクトを用いた例
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
簡単なアンケート(Survey)を取るためのアプリケーションがあったとします。

しかしこのアンケートシステムの営業担当は顧客に対して寛容な心を持っており、顧客の要望全てに答えようとしてしまいます。

エンジニアであるあなたは変更のあるたびにモデルフィールドの追加/削除を求められ、挙句の果てに
やれラベルを変更してほしい、ヘルプテキストを変更してほしいなどと変更を迫られます。

そんなときこそdefinable-serializerが真価を発揮します。

はじめに、アンケートをとるためのプロジェクトとsurveysアプリケーションを作成します


.. warning::

    ここではある程度djangoとrestframeworkの扱い方を知っている人を対象とします。
    また、インストール方法を読んでいない方は先に読んで準備を整えてください。


exampleプロジェクトとsurveysアプリケーションの作成と準備
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

以下のコマンドを実行してexampleプロジェクトとsurveysアプリケーションを作成します。

.. code-block:: shell

    $ django-admin.py startproject example_projecet
    $ cd ./example_projecet
    $ ./manage.py startapp surveys


次に ``settings.py`` 中の ``INSTALLED_APPS`` を変更します。

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'rest_framework',
        'codemirror2',
        'definable_serializer',
        'surveys',
    )


models.py と admin.py の変更
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

次に出来上がったsurveysアプリケーション中にあるmodels.pyを変更して、アンケートの設問を扱うモデルを用意します。

(Surveyモデルは、``models.Model`` ではなく ``AbstractDefinitiveSerializerModel`` を継承している点に注意してください)


.. code-block:: python

    # surveys/models.py
    from django.db import models
    from django.conf import settings
    from definable_serializer.models import (
        DefinableSerializerByYAMLField,
        AbstractDefinitiveSerializerModel,
    )
    from definable_serializer.models.compat import YAMLField


    class Survey(AbstractDefinitiveSerializerModel)
        title = models.CharField(
            null=False,
            blank=False,
        )

        # YAMLで定義されたシリアライザーを扱うフィールド
        question = DefinableSerializerByYAMLField()

        def __str__(self):
            return self.title


次にシリアライザーの定義を確認可能にするためのadmin.pyを用意します。
(admin.ModelAdminではなく、DefinableSerializerAdminを継承している点に注意してください)


.. code-block:: python

    # surveys/admin.py
    from django.contrib import admin
    from definable_serializer.admin import DefinableSerializerAdmin
    from surveys import models as surveys_models

    @admin.register(surveys_models.Survey)
    class SurveyAdmin(DefinableSerializerAdmin):
        list_display = (
            "id",
            "title",
        )

        list_display_links = (
            "id",
            "title",
        )


準備が完了したら以下のコマンドを実行して
`http://localhost:8000/admin/surveys/survey/add/survey <http://localhost:8000/admin/surveys/survey/add/survey>`_
をブラウザーで開き、モデルのadmin画面にアクセスしましょう。

.. code-block:: python

    $ ./manage.py makemigrations
    $ ./manage.py migrate

    $ ./manage.py createsuperuser
    Username (leave blank to use 'traincrash'): admin
    Email address: admin@example.com
    Password: <password>
    Password (again): <password>
    Superuser created successfully.

    $ ./manage.py runserver 0.0.0.0:8000
    Django version 1.11.6, using settings 'example_project.settings'
    Starting development server at http://0.0.0.0:8000/
    Quit the server with CONTROL-C.
