from itertools import chain
from operator import attrgetter
import os
import re

from .theme import Theme
from flask import current_app
from flask.ext.assets import Environment
from webassets.env import RegisterError


IDENTIFIER = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*$')


def starchain(i):
    return chain(*i)


def list_folders(path):
    """A helper function that only returns the directories in a given folder.

    :param path: The path to list directories in.
    """
    return (name for name in os.listdir(path)
            if os.path.isdir(os.path.join(path, name)))


def load_themes_from(path):
    """Used by default loaders. Provide a path, and it will find valid themes,
    yielding them one by one.

    :param path: The path to search for themes in.
    """
    for basename in (b for b in list_folders(path) if IDENTIFIER.match(b)):
        try:
            t = Theme(os.path.join(path, basename))
        except:
            pass
        else:
            if t.identifier == basename:
                yield t


def packaged_themes_loader(app):
    """Finds themes that are shipped with the application. It will
    look in the application's root path for a ``themes`` directory - for
    example, the ``someapp`` package can ship themes in the directory
    ``someapp/themes/``.
    """
    themes_path = os.path.join(app.root_path, 'themes')
    if os.path.exists(themes_path):
        return load_themes_from(themes_path)
    else:
        return ()


def theme_paths_loader(app):
    """Checks the app's `THEME_PATHS` configuration variable to find
    directories that contain themes. The theme's identifier must match the
    name of its directory.
    """
    theme_paths = app.config.get('THEME_PATHS', ())
    if isinstance(theme_paths, str):
        theme_paths = [p.strip() for p in theme_paths.split(';')]
    return starchain(load_themes_from(path) for path in theme_paths)


class ThemeManager(object):
    """
    This is responsible for loading and storing all the themes for an
    application. Calling `refresh` will cause it to invoke all of the theme
    loaders.

    A theme loader is simply a callable that takes an app and returns an
    iterable of `Theme` instances. You can implement your own loaders if your
    app has another way to load themes.

    :param app:     The app to bind to.
    :param app_id:  The value that the info.yaml's `application` key
                    is required to have. If you require a more complex
                    check, you can subclass and override the
                    `valid_app_id` method.
    :param loaders: An list of loaders to use. The defaults are
                    `packaged_themes_loader` and `theme_paths_loader`, in that
                    order.
    :kwarg log:     boolean to log refresh & bundle events to app, defaults True
    """
    extensions_filters = {'.css': 'cssmin', '.js': 'rjsmin'}

    def __init__(self, app, app_id, loaders=None, **kwargs):
        self.app = app
        self.app_id = app_id
        self._themes = None
        self.loaders = []
        if loaders:
            self.loaders.extend(loaders)
        else:
            self.loaders.extend((packaged_themes_loader, theme_paths_loader))
        self.asset_env = self.set_asset_env()
        self.log = kwargs.pop('log', True)
        self.refresh()

    def set_asset_env(self):
        if hasattr(self.app.jinja_env, 'assets_environment'):
            return self.app.jinja_env.assets_environment
        else:
            return Environment(self.app)

    @property
    def themes(self):
        """
        This is a dictionary of all the themes that have been loaded. The keys
        are the identifiers and the values are `Theme` objects.
        """
        if self._themes is None:
            self.refresh()
        return self._themes

    @property
    def list_themes(self):
        """
        This yields all the `Theme` objects, in sorted order.
        """
        return sorted(self.themes.values(), key=attrgetter('identifier'))

    def valid_app_id(self, app_id):
        """
        This checks whether the application identifier given will work with
        this application. The default implementation checks whether the given
        identifier matches the one given at initialization.

        :param app_id: The application identifier to check.
        """
        return self.app_id == app_id

    def register_theme_assets(self):
        for t in self.list_themes:
            for k,v in self.extensions_filters.items():
                manifest_entry, bundle = t.return_bundle(k,v)
                if self.log:
                    self.app.logger.info("{}".format(manifest_entry))
                if bundle:
                    bundle_name = "{}_{}".format(t.identifier, k[1:])
                    if bundle_name in self.asset_env:
                        pass
                    else:
                        try:
                            self.asset_env.register(bundle_name, bundle)
                        except RegisterError as e:
                            raise e

    def refresh(self):
        """Loads all of the themes into the `themes` dictionary. The loaders
        are invoked in the order they are given, so later themes will override
        earlier ones. Any invalid themes found (for example, if the
        application identifier is incorrect) will be skipped.
        """
        self._themes = {}
        for theme in starchain(ldr(self.app) for ldr in self.loaders):
            if self.valid_app_id(theme.application):
                self.themes[theme.identifier] = theme
        self.register_theme_assets()
