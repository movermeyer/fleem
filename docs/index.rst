============
Flask-Fleem
============
.. currentmodule:: flask_fleem

Flask-Fleem makes it easy for your application to support a wide range of
appearances.

.. contents::
   :local:
   :backlinks: none


Writing Themes
==============
A theme is simply a folder containing static media (like CSS files, images,
and JavaScript) and Jinja2 templates, with some metadata. A theme folder
should look something like this:

.. sourcecode:: text

    my_theme/
        info.yaml
        templates/
            layout.html
            index.html
        static/
            style.css

The ``info.yaml`` file contains the theme's metadata, so that the application
can provide a nice switching interface if necessary. ``static`` is
served directly to clients, and ``templates`` contains the Jinja2 template
files.

Note that exactly what templates you need to create will vary between
applications. Check the application's docs (or source code) to see what you
need.


Writing Templates
-----------------
Flask uses the Jinja2 template engine, so you should read `its documentation`_
to learn about the actual syntax of the templates.

All templates loaded from a theme will have a global function named `theme`
available to look up the theme's templates. For example, if you want to
extend, import, or include another template from your theme, you can use
``theme(template_name)``, like this:

.. sourcecode:: html+jinja

    {% extends theme('layout.html') %}
    {% from theme('_helpers.html') import form_field %}

If the template you requested doesn't exist within the theme, it will fall
back to using the application's template. If you pass `false` as the second
parameter, it will only return the theme's template.

.. sourcecode:: html+jinja

    {% include theme('header.html', false) %}

You can still import/include templates from the application, though. Just use
the tag without calling `theme`.

.. sourcecode:: html+jinja

    {% from '_helpers.html' import link_to %}
    {% include '_jquery.html' %}

You can also get the URL for the theme's media files with the `theme_static`
function:

.. sourcecode:: html+jinja

    <link rel=stylesheet href="{{ theme_static('style.css') }}">

.. _its documentation: http://jinja.pocoo.org/2/documentation/templates


``info.yaml`` Fields
--------------------
``name`` : required
    This is the full human readable name of the theme

``identifier`` : required
    The theme's identifier. It should be a Python identifier (starts with a
    letter or underscore, the rest can be letters, underscores, or numbers)
    and should match the name of the theme's folder.

``application`` : required
    The application identifier for the application the theme belongs to.

.. _Pygments: http://pygments.org/


Using the Extension in Your Application 
=======================================
To use with your application immediately:

    app = Flask(__name__)
    Fleem(app=app)
    
To use with an application at some further point:

    app = Flask(__name__)
    f = Fleem(options)
    f.init_app(app=app)
    
Options that may be passed to the Fleem constructor:

    loaders: default is None, and uses extension defaults
    app_identifier: default is None
    manager_cls: default is `ThemeManager`
    theme_url_prefix: default is "/_themes"


.. warning::

   Since the "Blueprints" mechanism of Flask 0.7 causes headaches in module
   compatibility mode, `setup_themes` will automatically register `_themes`
   as a blueprint and not as a module if possible. If this causes headaches
   with your application, then you need to either (a) upgrade to Flask 0.7 or
   (b) set ``Flask<0.7`` in your requirements.txt file.


Theme Loaders
-------------
`setup_themes` takes a few arguments, but the one you will probably be using
most is `loaders`, which is a list of theme loaders to use (in order) to find
themes. The default theme loaders are:

* `packaged_themes_loader`, which looks in your application's ``themes``
  directory for themes (you can use this to ship one or two default themes
  with your application)
* `theme_paths_loader`, which looks at the `THEME_PATHS` configuration
  setting and loads themes from each folder therein

It's easy to write your own loaders, though - a loader is just a callable that
takes an application instance and returns an iterable of `Theme` instances.
You can use the `load_themes_from` helper function to yield all the valid
themes contained within a folder. For example, if your app uses an "instance
folder" like `Zine`_ that can have a "themes" directory::

    def instance_loader(app):
        themes_dir = os.path.join(app.instance_root, 'themes')
        if os.path.isdir(themes_dir):
            return load_themes_from(themes_dir)
        else:
            return ()

.. _Zine: http://zine.pocoo.org/


Rendering Templates
-------------------
Once you have the themes set up, you can call in to the theme machinery with
`render_theme_template`. It works like `render_template`, but takes a `theme`
parameter before the template name. Also, `static_file_url` will generate a
URL to the given static file.

When you call `render_theme_template`, it sets the "active template" to the
given theme, even if you have to fall back to rendering the application's
template. That way, if you have a template like ``by_year.html`` that isn't
defined by the current theme, you can still

* extend (``{% extends theme('layout.html') %}``)
* include (``{% include theme('archive_header.html') %}``)
* import (``{% from theme('_helpers.html') import show_post %}``)

templates defined by the theme. This way, the theme author doesn't have to
implement every possible template - they can define templates like the layout,
and showing posts, and things like that, and the application-provided
templates can use those building blocks to form the more complicated pages.


Selecting Themes
----------------
How exactly you select the theme will vary between applications, so
Flask-Themes doesn't make the decision for you. If your app is any larger than
a few views, though, you will probably want to provide a helper function that
selects the theme based on whatever (settings, logged-in user, page) and
renders the template. For example::

    def get_current_theme():
        if g.user is not None:
            ident = g.user.theme
        else:
            ident = current_app.config.get('DEFAULT_THEME', 'plain')
        return get_theme(ident)
    
    def render(template, **context):
        return render_theme_template(get_current_theme(), template, **context)


.. warning::
   
   Make sure that you *only* get `Theme` instances from the theme manager. If
   you need to create a `Theme` instance manually outside of a theme loader,
   that's a sign that you're doing it wrong. Instead, write a loader that can
   load that theme and pass it to the extension setup, because if the theme is not
   loaded by the manager, then its templates and static files won't be
   available, which will usually lead to your application breaking.


API Documentation
=================
This API documentation is automatically generated from the source code.

.. autoclass:: Fleem
    :members:

.. autoclass:: Theme
    :members:

.. autofunction:: setup_themes

.. autofunction:: render_theme_template

.. autofunction:: static_file_url

.. autofunction:: get_theme

.. autofunction:: get_themes_list


Loading Themes
--------------
.. autoclass:: ThemeManager
   :members:

.. autofunction:: packaged_themes_loader

.. autofunction:: theme_paths_loader

.. autofunction:: load_themes_from
