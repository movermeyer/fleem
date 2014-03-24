from unittest import TestCase
from os.path import join, dirname
from flask import Flask
from flask_fleem import Fleem


class FleemTest(TestCase):
    TESTS = dirname(__file__)

    def setUp(self):
        app = Flask(__name__)
        app.config['THEME_PATHS'] = [join(self.TESTS, 'morethemes')]
        Fleem(app, app_identifier='testing')
        self.test_manager = ThemeManager(app, 'testing')
        self.app = app
