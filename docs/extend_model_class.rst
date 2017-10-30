.. _`extend_model_class`:


==============================================================================
提供するモデルクラス
==============================================================================

definable-serializerでは、 :ref:`definable-serializer-fields` で紹介したシリアライザーの定義を記述するためのモデルフィールドを提供しています。

このシリアライザー定義用フィールドからシリアライザークラスを取り出すには、2つの方法があります。

1つめは定義用フィールドからYAML/JSON文字列を取り出し、
``definable_serializer.serializers`` が持つ ``build_serializer_by_yaml`` 関数に渡す方法です。

2つめは ``AbstractDefinitiveSerializerModel`` を継承したモデルクラスを用意する方法です。


AbstractDefinitiveSerializerModel
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. class:: AbstractDefinitiveSerializerModel(*args, **kwargs)

このモデルクラスは ``django.db.models.Model`` を親クラスとしており、
``__init__`` メソッドの中で :ref:`definable_serializer_by_yaml_field_class` および
:ref:`definable_serializer_by_json_field_class` を利用しているフィールドを自動で探し、
``get_<フィールド名>_serializer_class`` というメソッドを付与します。

また、モデルクラスは複数のシリアライザー定義用のフィールドを持つことも可能です。

以下のようなモデルクラスを定義した場合、 ``get_foo_serializer_class`` と ``get_bar_serializer_class``
という2つのメソッドが自動でモデルオブジェクトに付与されます。


.. code-block:: python

    from definable_serializer.models import (
        DefinableSerializerByYAMLField,
        DefinableSerializerByJSONField,
        AbstractDefinitiveSerializerModel,
    )

    class MyModel(AbstractDefinitiveSerializerModel):
        ...

        foo = DefinableSerializerByYAMLField()
        bar = DefinableSerializerByJSONField()


.. code-block:: python

    >>> my_model = MyModel.objects.get(pk=1)
    >>> my_model.get_foo_serializer_class
    function
    >>> my_model.get_bar_serializer_class
    function
    >>> my_model.get_foo_serializer_class()
    NameEntry():
        first_name = CharField(max_length=100, required=True)
        last_name = CharField(max_length=100, required=True)

    >>> my_model.get_bar_serializer_class()
    Group():
        group_name = CharField(label='Group name', required=True)
        persons = Person(many=True):
            first_name = CharField(required=True)
            last_name = CharField(required=True)
