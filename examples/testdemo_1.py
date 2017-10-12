# coding: utf-8

from demo import GetImageCaptcha, PostApiV2UsersLogin
import unittest
from service import Service


class TestDemo(unittest.TestCase):
    def setUp(self):
        self.service = Service()

    def test_demo_1(self):
        GetImageCaptcha(service=self.service)
        PostApiV2UsersLogin(service=self.service, params=dict(identity='13381712936', password='welcome1'),
                            response=dict(result='success'))
