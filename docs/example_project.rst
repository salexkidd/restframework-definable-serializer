.. _example_project:


==============================================================================
アプリケーションにdefinable-serializerを組み込む
==============================================================================

definable-serializerの一番の目的は、数多ある入力項目の仕様変更からエンジニアを守ることです。
故にシリアライザーの定義をファイルに書いては意味がありません。

その問題を解決する一番の方法はWebインターフェイスです。
我々はrestframeworkを利用している時点でdjangoを利用しています。
そしてdjangoには初めからadmin画面が用意されています。

djangoはadmin画面にてモデルの追加/変更/削除を簡単に行うことができます。
それを利用してモデルにシリアライザーの定義を保存するためのフィールドを追加し、
admin画面を用意すれば簡単にシリアライザーの定義を変更することができます。

これでデプロイをすることなくシリアライザーを簡単に変更することができます。
definable-serializerではシリアライザー定義を扱うためのフィールドを用意しています。


------------------------------------------------------------------------------


シリアライザーを定義するためのモデルフィールド
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

definable-serializerではモデルにYAML/JSONでシリアライザー定義を扱うための ``DefinableSerializerByYAMLField`` と ``DefinableSerializerByJSONField``
という2つのモデルフィールドを用意しています。

これらのフィールドを利用すると、admin画面中にCodeMirror2のウィジェットでラップされたテキストエリアが現れます。

さらにadmin画面中で記述されたシリアライザーの定義を確認するための機能を提供する ``DefinableSerializerAdmin``
クラスを提供しています。ここでは簡単なプロジェクトを作成し、組込例を紹介します。


------------------------------------------------------------------------------


アンケートシステムを作成してadmin画面でシリアライザーを定義する
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
簡単なアンケート(Survey)を取るためのアプリケーションがあるとします。

しかしこのアンケートシステムの営業担当は顧客に対して寛容な心を持ち、顧客の要望全てに答えようとしてしまいます。
担当のエンジニアは変更のあるたびにモデルフィールドの追加/削除を求められ、
挙句の果てにラベルやヘルプテキストの変更など、ありとあらゆる要望に答えなくてはなりません。

そんなときこそdefinable-serializerが真価を発揮します。

ここではアンケートをとるためのプロジェクトとsurveysアプリケーションを作成し、definable-serializeの組み込み方を説明します。

.. warning::

    ここではある程度djangoとrestframeworkの扱いを知っている方を対象とします。
    また、インストール方法を読んでいない方は先に読んで準備を整えてください。

    このサンプルアプリケーションは完全に動作するものではありません。実際に動作するものを確認したい場合は、
    `完全に動作するExampleプロジェクトを用意しています。 <https://github.com/salexkidd/restframework-definable-serializer-example>`_
    そちらを参照してください。


exampleプロジェクトとsurveysアプリケーションの作成と準備
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

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


models.pyとadmin.pyの変更
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

今回作成するのはアンケートシステムなので、アンケートの質問を扱う ``Survey`` モデルと、回答データを
扱うための ``Answer`` モデルを用意します。

Surveyモデル
    Surveyモデルには先ほど紹介した ``DefinableSerializerByYAMLField`` を利用して質問用のシリアライザー定義を取り扱う ``question`` フィールドと、
    アンケートタイトルを扱う ``title`` フィールドを追加します。

Answerモデル
    Answerモデルには回答対象へリレーションを張るための ``survey`` フィールドと、
    回答データを保持する ``answer`` フィールドを追加します。


models.pyを作成する
******************************************************************************

*surveys/models.py* を変更します。

Surveyモデルは、``models.Model`` ではなく ``AbstractDefinitiveSerializerModel``
を継承している点に注意してください。

.. code-block:: python

    # surveys/models.py
    from django.db import models
    from django.conf import settings
    from definable_serializer.models import (
        DefinableSerializerByYAMLField,
        AbstractDefinitiveSerializerModel,
    )
    from definable_serializer.models.compat import YAMLField


    class Survey(AbstractDefinitiveSerializerModel):
        title = models.CharField(
            null=False,
            blank=False,
            max_length=300,
        )

        # YAMLで定義されたシリアライザーを扱うフィールド
        question = DefinableSerializerByYAMLField()

        def __str__(self):
            return self.title


    class Answer(models.Model):
        survey = models.ForeignKey("Survey")

        respondent = models.ForeignKey(
            settings.AUTH_USER_MODEL,
            on_delete=models.CASCADE,
        )

        answer = YAMLField(
            null=False,
            blank=False,
            default={},
            verbose_name="answer data",
            help_text="answer data"
        )

        class Meta:
            unique_together = ("survey", "respondent",)


admin.pyを作成する
******************************************************************************

admin画面にsurveyモデルを変更する画面を表示するため、 *surveys/admin.py* を変更します。
AnswerAdminクラスは、admin.ModelAdminではなく、 ``DefinableSerializerAdmin``
を継承している点に注意してください


.. code-block:: python

    # surveys/admin.py
    from django.contrib import admin
    from definable_serializer.admin import DefinableSerializerAdmin
    from surveys import models as surveys_models

    @admin.register(surveys_models.Survey)
    class SurveyAdmin(DefinableSerializerAdmin):
        list_display = ("id", "title",)
        list_display_links = ("id", "title",)


    @admin.register(surveys_models.Answer)
    class AnswerAdmin(DefinableSerializerAdmin):
        list_display = ("id", "survey", "respondent",)
        list_display_links = ("id", "survey",)


作業が完了するとadmin画面からSurveyモデルとAnsweモデルの変更を行うことができるようになります。


質問用のシリアライザー定義を記述する
******************************************************************************

admin画面を確認するために開発用サーバーを起動します。初回の起動となるためマイグレーション作業及びadminアカウントを作成します。

.. code-block:: shell

    $ ./manage.py makemigrations
    ...

    $ ./manage.py migrate
    ...

    $ ./manage.py createsuperuser
    Username (leave blank to use 'your-name'): admin
    Email address: admin@example.com
    Password: <password>
    Password (again): <password>
    Superuser created successfully.

    $ ./manage.py runserver 0.0.0.0:8000
    Django version 1.11.6, using settings 'example_project.settings'
    Starting development server at http://0.0.0.0:8000/
    Quit the server with CONTROL-C.


開発用サーバーが起動したら
`http://localhost:8000/admin/surveys/survey/add/survey <http://localhost:8000/admin/surveys/survey/add/>`_
をブラウザーで開いてSurveyモデルのadmin画面にアクセスしましょう。

タイトルとYAMLで書かれたシリアライザー定義を入力します。ここでは名前、年齢、性別の3つを扱う簡単なシリアライザーを利用しましょう。
以下のYAMLデータをQuestionにコピー＆ペーストしてください。(タイトルは適当で構いません)

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


入力が完了したら、保存して[編集を続けるボタン]ボタンを押します。すると、編集画面の上部に定義されたシリアライザーの状態が表示されます。

.. figure:: imgs/survey_admin_editing.png

    保存後に問題がなければ実際にシリアライザークラスの情報が表示されます。

また、定義されたシリアライザーをrestframeworkのもつBrowsable APIのページを使って確認をすることもできます。

タイトルラインにある (Show Restframework Browsable Page) のリンクをクリックすると、
Browsable API画面が開き、YAMLで定義されたシリアライザーの入力テストを行うことができます。

.. figure:: imgs/serializer_with_browsable_api.png

    Browsable APIで確認した例


定義が確認できたところで、次はシリアライザーの定義を変更してみましょう。
ここでは紹介文用のテキストエリアを提供するフィールド、 ``introduction`` を追加します。

.. code-block:: yaml

    main:
      name: EnqueteSerializer
      fields:

      ...

      - name: introduction
        field: definable_serializer.extra_fields.TextField
        field_args:
          required: true
          placeholder: Hello!


追加が完了したら再度 Browsable APIでシリアライザーの状態を確認してみましょう。
問題がなければ、テキストエリアが追加されます。

.. figure:: imgs/add_textarea_to_serializer_with_browsable_api.png

    定義が正しければテキストエリアが追加されます

次はユーザーがアンケートの回答を行うビューを作成してユーザーからの入力を受け付ける画面を作成します。


------------------------------------------------------------------------------


ユーザーからの回答を受け付けるビュー
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

restframeworkを利用する場合、REST API経由でやり取りをするケースが多いと思いますが、
ここではrestframeworkが持つ ``TemplateHTMLRenderer`` も同時にサポートしてユーザーの回答画面を作成します。

このビューにおいて重要になるのは、モデルオブジェクト中のシリアライザー定義からシリアライザークラスを取り出すことと、
POSTされた回答内容をどのように保存するかという2点です。以下に2点の解決方法を示します。


.. _`extract_serializer_by_model_field`:

モデルからシリアライザークラスを取り出す方法
******************************************************************************

シリアライザー定義用フィールドを持つモデルオブジェクトからシリアライザーをクラスを取得するのはさほど難しくありません。

先ほど定義したSurveyモデルクラスは　``AbstractDefinitiveSerializerModel`` を継承しており、
そこにシリアライザークラスを取り出すためのメソッドが自動的に追加される方法が組み込まれているからです。

例として先ほど作成したSurveyモデルオブジェクトから ``question`` フィールドに記述されたシリアライザー定義から、
シリアライザークラスを取得します。

.. code-block:: python

    >>> from surveys import models as surveys_models
    >>> survey_obj = surveys_models.Survey.objects.get(pk=1)
    >>> question_serializer_kls = survey_obj.get_question_serializer_class()
    >>> question_serializer = question_serializer_kls()
    >>> print(question_serializer)
    EnqueteSerializer():
        name = CharField(max_length=100, required=True)
        age = IntegerField(required=True)
        gender = ChoiceField([['male', '男性'], ['female', '女性']], required=True)
        introduction = TextField(placeholder='Hello!', required=True)

.. hint::

    例えば ``foobar`` というモデルフィールドが上記のフィールドのうちどちらかを利用していたら、
    ``get_foobar_serializer_class`` というメソッド名でシリアライザークラスを取り出すことができます。
    (ただし、モデルクラスが ``AbstractDefinitiveSerializerModel`` を継承している場合のみに限ります)


.. _`storing-input-data`:

入力された内容を保存する方法
******************************************************************************

definable-serializerでは、モデルのフィールドとシリアライザーのフィールドを対にしないという理念のもと作られています。
そのため、入力内容をモデルの単一のフィールドに保存する必要があります。

以下にsurveys/models.pyに定めたAnswerクラスにアンケートの内容を保存するためのコード例を示します。


.. code-block:: python

    # シリアライザークラスを作成してデータを渡し、バリデーションを行う
    >>> from surveys import models as surveys_models
    >>> survey_obj = surveys_models.Survey.objects.get(pk=1)
    >>> question_serializer_kls = survey_obj.get_question_serializer_class()
    >>> question_serializer = question_serializer_kls(data={
    ...     "name": "John Smith",
    ...     "age": 20,
    ...     "gender": "male",
    ...     "introduction": "Hi!"
    ... })
    >>> question_serializer.is_valid()
    True

    >>> from django.contrib.auth import get_user_model
    >>> admin_user = get_user_model().objects.get(pk=1)
    >>> print(admin_user)
    admin
    >>> answer_obj = surveys_models.Answer.objects.create(
    ...     survey=survey_obj,
    ...     respondent=admin_user,
    ...     answer=question_serializer.validated_data
    ... )
    >>> answer_obj.answer
    odict_values(['John Smith', 20, 'male', 'Hi!'])


実際に入れたデータをadmin画面で確認してみましょう。YAML形式で保存されていることが確認できます。

.. figure:: imgs/data_store_by_yaml.png

    `!!Ordered Mapping <http://yaml.org/type/omap.html>`_ で保存されていることが確認できます。

.. hint::
    例としてYAMLFieldを用いてバリデーション後の結果を保存しましたが、
    モデルフィールドさえ提供されていれば、JSONやPickle等で保存することが出来ます。
    詳しくは :ref:`methods-of-storing-input-data` を参照してください


.. danger::

    特にPostgreslを利用しており、保存されているJSONデータを検索の対象としたい場合はdjangoの提供する
    ``postgres.fields.JSONField`` を利用することをおすすめします。
    ただし、そのままではいくつかの問題があります。詳しくは :ref:`json-field-problem` を御覧ください。

回答用ビューの作成例
******************************************************************************

上の内容を踏まえて回答用のビューを作成例を示します。


.. warning::
    下記のViewのコードは作成例です。
    urls.pyへの登録、テンプレートの用意、登録後のリダイレクト先が存在しないため、そのままでは正しく動作しません。
    ここではそれらが完全に揃っていることにして説明を続けます。

    実際に動作するものを確認したい場合は
    `完全に動作するExampleプロジェクトを用意しています <https://github.com/salexkidd/restframework-definable-serializer-example>`_


.. code-block:: python

    from django.contrib import messages
    from django.http import HttpResponseRedirect
    from django.shortcuts import get_object_or_404

    from rest_framework.views import APIView
    from rest_framework.response import Response
    from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
    from rest_framework.exceptions import MethodNotAllowed, NotFound
    from rest_framework.permissions import IsAuthenticated
    from rest_framework.authentication import (
        SessionAuthentication, TokenAuthentication
    )

    from . import models as surveys_models


    class Answer(APIView):
        """
        Answer API
        """
        allowed_methods = ("GET", "POST", "OPTIONS",)
        renderer_classes = (TemplateHTMLRenderer, JSONRenderer,)
        authentication_classes = (SessionAuthentication, TokenAuthentication,)
        permission_classes = (IsAuthenticated,)
        template_name = 'answer.html'

        def _get_previous_answer(self, survey):
            """
            過去の回答データを取得します。存在しない場合はNoneを返します
            """
            previous_answer = None
            try:
                previous_answer = surveys_models.Answer.objects.get(
                    respondent=self.request.user, survey=survey)
            except surveys_models.Answer.DoesNotExist:
                pass

            return previous_answer

        def initial(self, request, *args, **kwargs):
            super().initial(request, *args, **kwargs)
            survey = get_object_or_404(
                surveys_models.Survey, pk=kwargs.get('survey_pk'))
            self.previous_answer = self._get_previous_answer(survey)
            self.survey = getattr(self.previous_answer, "survey", None) or survey

        def get_serializer(self, *args, **kwargs):
            """
            質問用のシリアライザークラスを返します
            """
            return self.survey.get_question_serializer_class()(*args, **kwargs)

        def get(self, request, survey_pk, format=None):
            """
            Request HeaderのAcceptが "application/json" の場合はJSONRendererで
            過去の入力データを返します。回答がない場合は404を返します。

            Request HeaderのAcceptが "application/json" 以外の場合、質問の入力画面を表示します。
            ユーザーが過去に同じ質問に回答していた場合、回答データを復元して表示します。
            """
            response = None
            serializer = self.get_serializer()
            if self.previous_answer:
                serializer = self.get_serializer(data=self.previous_answer.answer)
                serializer.is_valid()

            if isinstance(self.request.accepted_renderer, TemplateHTMLRenderer):
                response = Response(
                    {'serializer': serializer, 'survey': self.survey})
            else:
                if not self.previous_answer:
                    raise NotFound()
                response = Response(serializer.data)

            return response

        def post(self, request, survey_pk):
            """
            回答データの投稿を受け付けます。入力内容に不備があった場合はそれぞれのレンダラーでエラーレスポンスを返します。

            回答データに問題がなく、TemplateHTMLRendererを利用する場合はトップ画面にリダイレクトします。
            JSONRendererの場合は成功レスポンスを返します。

            また、過去に投稿がない場合は新しくAnswerオブジェクトを作成し、投稿があった場合はAnswerオブジェクトを更新します。
            """
            response = None
            serializer = self.get_serializer(data=self.request.data)

            if isinstance(self.request.accepted_renderer, TemplateHTMLRenderer):
                response = HttpResponseRedirect("/")
                if not serializer.is_valid():
                    response = Response(
                        {'serializer': serializer, 'survey': self.survey})
                else:
                    messages.add_message(
                        request, messages.SUCCESS, 'Thank you for posting! 💖')
            else:
                serializer.is_valid(raise_exception=True)
                response = Response(serializer.data)

            if serializer.is_valid():
                if self.previous_answer:
                    self.previous_answer.answer = serializer.validated_data
                    self.previous_answer.save()
                else:
                    surveys_models.Answer.objects.create(
                        survey=self.survey,
                        respondent=request.user,
                        answer=serializer.validated_data
                    )

            return response

        def options(self, request, *args, **kwargs):
            """
            APIスキーマやその他のリソース情報を返します。
            ただし、Request HeaderのAcceptが "text/html"の場合は 405(Method Not Allowed)を返します。
            """
            if request.accepted_media_type == TemplateHTMLRenderer.media_type:
                raise MethodNotAllowed(
                    "It can not be used except when "
                    "it is content-type: application/json."
                )
            return super().options(request, *args, **kwargs)


------------------------------------------------------------------------------


回答用ビューのへのアクセス例
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


ブラウザーでレスポンスを得た場合
******************************************************************************

上記のビューにブラウザーからアクセスすると以下のような画面を返します。


.. figure:: imgs/survey_answer_view_with_browser.png

    回答画面のイメージ


Postmanを用いてREST API経由のレスポンスを得た場合
******************************************************************************

`Chromeの機能拡張であるPostman <https://chrome.google.com/webstore/detail/postman/fhbjgbiflinjbdggehcddcbncdddomop?hl=ja>`_
を用いてREST API経由で回答を行った場合の画面を示します。


.. figure:: imgs/survey_answer_view_with_postman.png


.. warning::

    REST API経由でアクセスを行う場合、Headersタブにて ``Accept``, ``Authorization``, ``Content-Type`` の3つを適切に指定する必要があります。

    .. figure:: imgs/postman_with_headers.png


PostmanでOPTIONSメソッドでレスポンスを得た場合
******************************************************************************

``OPTIONS`` メソッドでアクセスするとREST APIの詳細情報及びPOST時のJSONスキーマが表示されます。
（ただし ``Accept``, ``Authorization``, ``Content-Type`` の3つを適切に指定する必要があります。）

以下にレスポンス例を示します。

.. code-block:: json

    {
        "name": "Answer",
        "description": "Answer API",
        "renders": [
            "text/html",
            "application/json"
        ],
        "parses": [
            "application/json",
            "application/x-www-form-urlencoded",
            "multipart/form-data"
        ],
        "actions": {
            "POST": {
                "name": {
                    "type": "string",
                    "required": true,
                    "read_only": false,
                    "label": "Name",
                    "max_length": 100
                },
                "age": {
                    "type": "integer",
                    "required": true,
                    "read_only": false,
                    "label": "Age"
                },
                "gender": {
                    "type": "choice",
                    "required": true,
                    "read_only": false,
                    "label": "Gender",
                    "choices": [
                        {
                            "value": "male",
                            "display_name": "男性"
                        },
                        {
                            "value": "female",
                            "display_name": "女性"
                        }
                    ]
                },
                "introduction": {
                    "type": "string",
                    "required": true,
                    "read_only": false,
                    "label": "Introduction"
                }
            }
        }
    }
