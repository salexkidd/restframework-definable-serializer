from setuptools import setup

with open("README.md") as f:
    long_description = f.read()

setup(
    name='restframework-definable-serializer',
    author = "salexkidd",
    author_email = "salexkidd@gmail.com",
    url = "https://github.com/salexkidd/restframework-definable-serializer",
    description='restframework-definable-serializer',
    long_description=long_description,
    keywords = ["django", "restframework", "serializer"],
    version='0.1',
    packages=['definable_serializer',],
    license="MIT",
    install_requires=[
        "djangorestframework>=3.7.0",
        "django-codemirror2>=0.2",
        "django-jsonfield>=1.0.1",
        "django-yamlfield>=1.0.3",
        "PyYAML>=3.12",
        "ruamel.yaml>=0.13.5",
        "simplejson>=3.11.1",
        "six>=1.11.0",
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
