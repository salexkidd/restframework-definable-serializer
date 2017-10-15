# restframework-definable-serializer

restframework-definable-serializer is definable serializer by JSON or YAML format.


# Feature
- It can define restframework serializer by JSON or YAML
- It can write and modify serializer by django admin pages.


# Dependencies
- python 3
- django >= 1.11
- djangorestframework>=3.7.0
- django-codemirror2>=0.2
- django-jsonfield>=1.0.1
- django-yamlfield>=1.0.3
- PyYAML>=3.12
- ruamel.yaml>=0.13.5
- simplejson>=3.11.1
- six>=1.11.0


# Quick start

1. Install restframework-definable-serializer

```
pip install restframework-definable-serializer
```

2. Add "definable_serializer" and "codemirror2" to your INSTALLED_APPS setting like this:

```
INSTALLED_APPS = [
    ...
    'definable_serializer',
    'codemirror2',

]
```

# samples
You can try restframework-definable-serializer. see example_project
