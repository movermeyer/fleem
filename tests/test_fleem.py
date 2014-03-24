from __future__ import with_statement
from os.path import dirname, join, abspath
from operator import attrgetter
from flask import Flask, url_for, render_template
from jinja2 import FileSystemLoader
from flask.ext.assets import Bundle
from webassets.env import RegisterError
from flask_fleem.fleem import (Fleem, static_file_url,
    template_exists, render_theme_template, get_theme, get_themes_list)
from flask_fleem.theme import Theme
from flask_fleem.theme_manager import ThemeManager, packaged_themes_loader, theme_paths_loader, load_themes_from
from . import FleemTest


class TestThemeObject(FleemTest):
    def test_theme(self):
        test_path = join(self.TESTS, 'themes', 'cool')
        cool = Theme(test_path)
        manifest, bundle = cool.return_bundle('.css', 'cssmin')
        self.assertEqual(cool.name, 'Cool Blue v1')
        self.assertEqual(cool.identifier, 'cool')
        self.assertEqual(cool.path, abspath(test_path))
        self.assertEqual(cool.random_attribute, "totally random")
        self.assertEqual(cool.static_path, join(cool.path, 'static'))
        self.assertEqual(cool.templates_path, join(cool.path, 'templates'))
        self.assertIsInstance(cool.jinja_loader, FileSystemLoader)
        self.assertIsInstance(bundle, Bundle)


class TestLoaders(FleemTest):
    def test_load_themes_from(self):
        test_path = join(self.TESTS, 'themes')
        themes_iter = load_themes_from(test_path)
        themes = list(sorted(themes_iter, key=attrgetter('identifier')))
        self.assertEqual(themes[0].identifier, 'cool')
        self.assertEqual(themes[1].identifier, 'notthis')
        self.assertEqual(themes[2].identifier, 'plain')

    def test_packaged_themes_loader(self):
        themes_iter = packaged_themes_loader(self.app)
        themes = list(sorted(themes_iter, key=attrgetter('identifier')))
        self.assertEqual(themes[0].identifier, 'cool')
        self.assertEqual(themes[1].identifier, 'notthis')
        self.assertEqual(themes[2].identifier, 'plain')

    def test_theme_paths_loader(self):
        themes = list(theme_paths_loader(self.app))
        self.assertEqual(themes[0].identifier, 'cool')


class TestSetup(FleemTest):
    def test_theme_manager(self):
        manager = ThemeManager(self.app, 'testing')
        self.assertIsInstance(self.app.extensions['fleem_manager'], ThemeManager)
        self.assertEqual(manager.themes['cool'].name, self.app.extensions['fleem_manager'].themes['cool'].name)
        self.test_manager.refresh()
        themeids = sorted(manager.themes.keys())
        self.assertEqual(themeids, ['cool', 'plain'])
        self.assertEqual(manager.themes['cool'].name, 'Cool Blue v2')

    def test_setup_themes(self):
        self.assertTrue(self.app.extensions['fleem_manager'])
        self.assertIn('_themes', self.app.blueprints)
        self.assertIn('theme', self.app.jinja_env.globals)
        self.assertIn('theme_static', self.app.jinja_env.globals)

    def test_get_helpers(self):
        with self.app.test_request_context('/'):
            cool = self.app.extensions['fleem_manager'].themes['cool']
            plain = self.app.extensions['fleem_manager'].themes['plain']
            self.assertIs(get_theme('cool'), cool)
            self.assertIs(get_theme('plain'), plain)
            tl = get_themes_list()
            self.assertIs(tl[0], cool)
            self.assertIs(tl[1], plain)
            with self.assertRaises(KeyError):
                get_theme('notthis')


class TestStatic(FleemTest):
    def test_static_file_url(self):
        with self.app.test_request_context('/'):
            url = static_file_url('cool', 'style.css')
            genurl = url_for('_themes.static', themeid='cool',
                             filename='style.css')
            self.assertEqual(url, genurl)


class TestTemplates(FleemTest):
    def test_template_exists(self):
        with self.app.test_request_context('/'):
            self.assertTrue(template_exists('hello.html'))
            self.assertTrue(template_exists('_themes/cool/hello.html'))
            self.assertFalse(template_exists('_themes/plain/hello.html'))

    def test_loader(self):
        ft = self.app.blueprints['_themes']
        with self.app.test_request_context('/'):
            src = ft.jinja_loader.get_source(
                self.app.jinja_env, '_themes/cool/hello.html')
            self.assertEqual(src[0].strip(), 'Hello from Cool Blue v2.')

    def test_render_theme_template(self):
        with self.app.test_request_context('/'):
            coolsrc = render_theme_template('cool', 'hello.html').strip()
            plainsrc = render_theme_template('plain', 'hello.html').strip()
            self.assertEqual(coolsrc, 'Hello from Cool Blue v2.')
            self.assertEqual(plainsrc, 'Hello from the application')

    def test_active_theme(self):
        with self.app.test_request_context('/'):
            appdata = render_template('active.html').strip()
            cooldata = render_theme_template('cool', 'active.html').strip()
            plaindata = render_theme_template('plain', 'active.html').strip()
            self.assertEqual(appdata, 'Application, Active theme: none')
            self.assertEqual(cooldata, 'Cool Blue v2, Active theme: cool')
            self.assertEqual(plaindata, 'Application, Active theme: plain')

    def test_theme_static(self):
        with self.app.test_request_context('/'):
            coolurl = static_file_url('cool', 'style.css')
            cooldata = render_theme_template('cool', 'static.html').strip()
            self.assertEqual(cooldata, 'Cool Blue v2, {}'.format(coolurl))

    def test_theme_static_outside(self):
        with self.app.test_request_context('/'):
            with self.assertRaises(RuntimeError):
                render_template('static.html')

    def test_theme_include_static(self):
        with self.app.test_request_context('/'):
            data = render_template('static_parent.html').strip()
            url = static_file_url('plain', 'style.css')
            self.assertEqual(data, 'Application, Plain, {}'.format(url))

    def test_extend(self):
        with self.app.test_request_context('/'):
            data = render_theme_template('cool', 'extending.html').strip()
            self.assertIsNotNone(data)
            self.assertEqual(data, 'hello I am theme_layout')
