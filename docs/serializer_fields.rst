=======================================
利用可能なシリアライザーフィールド
=======================================


.. _`serializer_fields`:


definable-serializerでは、restframeworkが提供する標準のフィールド以外にも、
外部パッケージで提供されるシリアライザーフィールドも利用可能です。

フィールドタイプを指定するには各フィールドの ``field`` にフィールドクラスを指定します。

またタイピング数を節約するため、restframeworkが提供するシリアライザーフィールドに限り、クラス名のみで指定が可能です。


.. code-block:: yaml

    main:
      name: Unit
      fields:
      - name: favorite_food
        field: CharField # restframeworkのシリアライザーフィールドクラス名 or <パッケージ名>.<モジュール名>.<クラス名>


フィールドクラスに引数を与える場合は ``field_args`` 及び ``field_kwargs`` を利用します。


.. code-block:: yaml

    - name: animal_choice_field
      field: ChoiceField
      field_args:
        - - - dog
            - 🐶Dog
          - - cat
            - 😺Cat
          - - rabbit
            - 🐰Rabbit
      field_kwargs:
        label: "Lovely Animals"
        help_text: "Please choice your favorite animal"
        required: true


------------------------------------------------------------------------------


restframeworkの提供するシリアライザーフィールド
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

2017-10月現在、definable-serializerでは ``DictField``, ``ListField`` 及び ``SerializerMethodField``
以外のシリアライザーフィールドが利用可能です。(これらのフィールドは将来的にサポートされる予定です)

シリアライザーフィールドの一覧については `restframeworkのシリアライザーのページを参照してください <http://www.django-rest-framework.org/api-guide/fields/#serializer-fields>`_


------------------------------------------------------------------------------


definable-serializerが提供するシリアライザーフィールド
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Zen Of Pythonの *暗示するより明示するほうがいい* と手間を省くという観点からdefinable-serializerでもいくつかのフィールドを提供しています。

特に **TemplateHTMLRenderer** を用いた際に利用するフィールドをいくつか提供しています。

CheckRequiredField
++++++++++++++++++++++++++++++++++++++

必ずチェックをしなければならないチェックボックスを提供します。ユーザーに規約の同意などを求める際などに利用可能です。

fieldには ``definable_serializer.extra_fields.CheckRequiredField`` を指定します。


.. code-block:: yaml

    main:
      name: MySerializer
      fields:
      - name: agreement
        field: definable_serializer.extra_fields.CheckRequiredField


MultipleCheckboxField
++++++++++++++++++++++++++++++++++++++

複数のチェックボックスを表示するフィールドを提供します。このクラスはrestframeworkのMultipleChoiceFieldをラップし、
styleを指定することで実現しています。

fieldには ``definable_serializer.extra_fields.MultipleCheckboxField`` を指定します。

``required`` を ``true`` にすると必須入力になります。

``inline`` を ``true`` にするとチェックボックスが横並びに表示されます。


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




NonNullableChoiceField
++++++++++++++++++++++++++++++++++++++

Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillu


RadioField
++++++++++++++++++++++++++++++++++++++

Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillu


TextField
++++++++++++++++++++++++++++++++++++++

Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillu
