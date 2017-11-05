.. _`extra_serializer_fields`:

==============================================================================
提供するシリアライザーフィールドクラス
==============================================================================

Zen Of Pythonの *暗示するより明示するほうがいい* という観点からdefinable-serializerでは
**TemplateHTMLRenderer** のためにいくつかのフィールドを提供しています。

.. warning::

    これらのフィールドは将来的に別パッケージとして提供される可能性があります。


------------------------------------------------------------------------------


CheckRequiredField
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

.. class:: CheckRequiredField(*args, **kwargs)

必ずOnをしなければならないチェックボックスを提供します。ユーザーの意思確認などを行いたい場合に利用します。

このクラスは restframeworkの ``BooleanField`` を継承してつくられています。
オプションについては `BooleanField <http://www.django-rest-framework.org/api-guide/fields/#booleanfield>`_ を参照してください。

シリアライザー定義のfieldには ``definable_serializer.extra_fields.CheckRequiredField`` を指定します。

.. code-block:: yaml

    main:
      name: Agreement
      fields:
      - name: agreement
        field: definable_serializer.extra_fields.CheckRequiredField


------------------------------------------------------------------------------


MultipleCheckboxField
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

.. class:: MultipleCheckboxField(choices, *args, required=False, inline=False, **kwargs)

複数のチェックボックスによる選択肢を表示するフィールドを提供します。

fieldには ``definable_serializer.extra_fields.MultipleCheckboxField`` を指定します。

- ``required`` を ``true`` にすると必須選択になります。
- ``inline`` を ``true`` にするとチェックボックスが横並びに表示されます。

このクラスはrestframeworkの ``MultipleChoiceField`` を継承してつくられています。その他のオプションについては
`MultipleChoiceField <http://www.django-rest-framework.org/api-guide/fields/#multiplechoicefield>`_ を参照してください。

.. code-block:: yaml

    main:
      name: YourFavoriteAnimal
      fields:
      - name: animal_choice_field
        field: definable_serializer.extra_fields.MultipleCheckboxField
        field_args:
        - - - dog
            - 🐶Dog
          - - cat
            - 😺Cat
          - - rabbit
            - 🐰Rabbit
        field_kwargs:
          inline: true
          required: true
          label: Lovely Animals
          help_text: Please choice your favorite animal

.. figure:: imgs/multiple_animal_choice.png

    インライン化されたMultipleCheckboxField


------------------------------------------------------------------------------


.. _`check_required_field`:

ChoiceRequiredField
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

.. class:: ChoiceRequiredField(choices, *args, **kwargs)

**0.1.12 で登場しました。**

選択必須のリストを提供します。

基本的な動作は ``ChoiceField`` と変わりませんがユーザーに選択を促すブランクチョイスを入れるため、 ``choices`` の1つ目の値が必ずnull値である必要があります。

このクラスは restframeworkの ``ChoiceField`` を継承してつくられています。その他のオプションについては
`ChoiceField <http://www.django-rest-framework.org/api-guide/fields/#choicefield>`_ を参照してください。

.. code-block:: yaml

    main:
      name: YourFavoriteAnimal
      fields:
      - name: animal_choice_field
        field: definable_serializer.extra_fields.ChoiceWithBlankField
        field_args:
        - - - null
            - "-------- Please Choice one 😉 --------"
          - - dog
            - 🐶Dog
          - - cat
            - 😺Cat
          - - rabbit
            - 🐰Rabbit
        field_kwargs:
          label: Lovely Animals
          blank_label: '-------- Please Choice 😉 --------'
          help_text: Please choice your favorite animal


------------------------------------------------------------------------------


ChoiceWithBlankField
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

.. warning::
    ChoiceWithBlankFieldクラスは廃止予定です。変わりに :ref:`check_required_field` を利用してください。

.. class:: MultipleCheckboxField(choices, *args, blank_label=None, **kwargs)

渡されたchoicesの選択にブランクチョイスを自動的に追加します。ブランクチョイスが選択された状態でバリデーションが
行われるとエラーになります。

fieldには ``definable_serializer.extra_fields.ChoiceWithBlankField`` を指定します。

- ``blank_label`` に文字列を渡すとダッシュの連続の代わりにその文字列がブランクチョイスの部分に表示されます。

このクラスは restframeworkの ``ChoiceField`` を継承してつくられています。その他のオプションについては
`ChoiceField <http://www.django-rest-framework.org/api-guide/fields/#choicefield>`_ を参照してください。

.. code-block:: yaml

    main:
      name: YourFavoriteAnimal
      fields:
      - name: animal_choice_field
        field: definable_serializer.extra_fields.ChoiceWithBlankField
        field_args:
        - - - dog
            - 🐶Dog
          - - cat
            - 😺Cat
          - - rabbit
            - 🐰Rabbit
        field_kwargs:
          label: Lovely Animals
          blank_label: '-------- Please Choice 😉 --------'
          help_text: Please choice your favorite animal

.. figure:: imgs/choice_with_blank_field.png

    blank_labelに文字を渡した例。blank_labelが空の場合は "---------" となります。


------------------------------------------------------------------------------


RadioField
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

.. class:: RadioField(choices, *args, inline=False, **kwargs)


ラジオボタンによる選択肢を表示するフィールドを提供します。

fieldには ``definable_serializer.extra_fields.RadioField`` を指定します。

- ``inline`` を ``true`` にするとチェックボックスが横並びに表示されます。

このクラスは restframeworkの ``ChoiceField`` を継承してつくられています。その他のオプションについては
`ChoiceField <http://www.django-rest-framework.org/api-guide/fields/#choicefield>`_ を参照してください。

.. code-block:: yaml

    main:
      name: YourFavoriteAnimal
      fields:
      - name: animal_choice_field
        field: definable_serializer.extra_fields.RadioField
        field_args:
        - - - dog
            - 🐶Dog
          - - cat
            - 😺Cat
          - - rabbit
            - 🐰Rabbit
        field_kwargs:
          inline: true
          required: true

.. figure:: imgs/radio_field.png

    インライン化されたRadioField


------------------------------------------------------------------------------


TextField
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

.. warning::
    TextFieldクラスは廃止予定です。変わりに `CharField` を利用してstyle引数を渡してください。
    詳しくは `field-styles <http://www.django-rest-framework.org/topics/html-and-forms/#field-styles>`_ を参照してください。

    また、placeholder引数は :ref:`field_i18n` 翻訳の対象になりません。

テキストエリアを提供します。

fieldには ``definable_serializer.extra_fields.TextField`` を指定します。

- ``rows`` に数値を渡すことででテキストエリアの行数を指定することができます。
- ``placeholder`` に文字列を渡すとプレースホルダー文字列を表示することができます。



このクラスは restframeworkの ``CharField`` を継承してつくられています。その他のオプションについては
`CharField <http://www.django-rest-framework.org/api-guide/fields/#charfield>`_ を参照してください。


.. figure:: imgs/text_field.png

    placeholderとrowsを設定した例
