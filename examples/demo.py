# coding: utf-8

from mte.orm import Model, ParamsField, DataField, FilesField, JsonField, ResponseField, AuthField, \
    PathField, HeadersField


class GetImageCaptcha(Model):
    __api__ = '/images/captcha.jpg'
    __host__ = 'https://cashloan-demo.dianrong.com'
    __method__ = 'GET'

    status_code = ResponseField(default=200)


class PostApiV2UsersLogin(Model):
    __api__ = '/api/v2/users/login'
    __host__ = 'https://cashloan-demo.dianrong.com'
    __method__ = 'POST'

    content_result = ResponseField()
    status_code = ResponseField(default=200)
    result = ResponseField(default='success')
    content_needCaptcha = ResponseField(default=False)
    password = DataField(default='welcome1')
    identity = DataField()




