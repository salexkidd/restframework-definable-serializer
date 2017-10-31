from setuptools import setup, find_packages

try:
    with open("README.md") as f:
        long_description = f.read()

except Exception as e:
    long_description = ""

setup(
    name='restframework-definable-serializer',
    author = "salexkidd",
    author_email = "salexkidd@gmail.com",
    url = "https://github.com/salexkidd/restframework-definable-serializer",
    description='restframework-definable-serializer',
    long_description=long_description,
    keywords = ["django", "restframework", "serializer"],
    version='0.1.10',
    packages=find_packages(),
    package_data={
        'definable_serializer': [
            'templates/admin/definable_serializer/*.html',
        ]},

    license="MIT",
    install_requires=[
        "django-codemirror2>=0.2",
        "jsonfield>=2.0.2",
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
