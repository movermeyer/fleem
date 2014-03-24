"""
Fleem
------------
Fleem provides infrastructure for theming support in Flask
applications:

- Loading themes
- Rendering templates from themes
- Serving static files like CSS and images from themes


Links
`````
* `documentation <http://packages.python.org/>`_
* `issues <https://github.com/thrisp/fleem/issues>`_
* `source version <https://github.com/thrisp/fleem>`_
"""
from setuptools import setup

setup(
    name='Flask-Fleem',
    version='0.0.5',
    url='http://github.com/thrisp/fleem',
    license='MIT',
    author='thrisp/hurrata',
    author_email='blueblank@gmail.com',
    description='Theming for Flask applications',
    long_description=__doc__,
    packages=['flask_fleem'],
    zip_safe=False,
    platforms='any',
    install_requires=['Flask>=0.9',
                      'Flask-Assets>=0.8',
                      'PyYAML>=3.10'],
    test_suite='nose.collector',
    tests_require=[
        'nose',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
