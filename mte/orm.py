# coding: utf-8

from client import HttpSession
from nose.tools import assert_equal, assert_greater_equal, assert_less_equal
import json
import sys
from logger import logger

reload(sys)
sys.setdefaultencoding('utf8')


def get_dict_res(dic, key):
    result = 'None'
    for k, v in dic.items():
        if k == key:
            result = v
        else:
            if isinstance(v, dict):
                result = get_dict_res(v, key)
            else:
                continue
    return result


class Field(object):
    def __init__(self, **kw):
        self.name = kw.get('name', None)
        self._default = kw.get('default', 'none')
        self.request_type = kw.get('request_type', None)
        self._max = kw.get('max', None)

    @property
    def default(self):
        d = self._default
        return d() if callable(d) else d


class AuthField(Field):
    def __init__(self, **kw):
        if not 'request_type' in kw:
            kw['request_type'] = 'auth'
        super(AuthField, self).__init__(**kw)


class PathField(Field):
    def __init__(self, **kw):
        if not 'request_type' in kw:
            kw['request_type'] = 'path'
        super(PathField, self).__init__(**kw)


class ParamsField(Field):
    def __init__(self, **kw):
        if not 'request_type' in kw:
            kw['request_type'] = 'params'
        super(ParamsField, self).__init__(**kw)


class DataField(Field):
    def __init__(self, **kw):
        if not 'request_type' in kw:
            kw['request_type'] = 'data'
        super(DataField, self).__init__(**kw)


class FilesField(Field):
    def __init__(self, **kw):
        if not 'request_type' in kw:
            kw['request_type'] = 'files'
        super(FilesField, self).__init__(**kw)


class JsonField(Field):
    def __init__(self, **kw):
        if not 'request_type' in kw:
            kw['request_type'] = 'json'
        super(JsonField, self).__init__(**kw)


class ResponseField(Field):
    def __init__(self, **kw):
        if not 'request_type' in kw:
            kw['request_type'] = 'res'
        super(ResponseField, self).__init__(**kw)

    @property
    def max(self):
        d = self._max
        return d() if callable(d) else d


class HeadersField(Field):
    def __init__(self, **kw):
        if not 'request_type' in kw:
            kw['request_type'] = 'headers'
        super(HeadersField, self).__init__(**kw)


class ModelMetaclass(type):
    def __new__(cls, name, bases, attrs):
        if name == 'Model':
            return type.__new__(cls, name, bases, attrs)

        # logger.info('Scan ORMapping %s...' % name)
        params = dict()
        data = dict()
        files = dict()
        json = dict()
        response = dict()
        headers = dict()
        path = dict()
        for k, v in attrs.items():
            # if isinstance(v, Field) -> 待扩展
            if isinstance(v, ParamsField):
                params[k] = v
                attrs.pop(k)
            elif isinstance(v, DataField):
                data[k] = v
                attrs.pop(k)
            elif isinstance(v, FilesField):
                files[k] = v
                attrs.pop(k)
            elif isinstance(v, JsonField):
                json[k] = v
                attrs.pop(k)
            elif isinstance(v, ResponseField):
                response[k] = v
                attrs.pop(k)
            elif isinstance(v, HeadersField):
                headers[k] = v
                attrs.pop(k)
            elif isinstance(v, PathField):
                path[k] = v
                attrs.pop(k)
        if '__api__' not in attrs:
            raise AttributeError('Not Found __api__ in: %s' % name)
        if '__method__' not in attrs:
            raise AttributeError('Not Found __method__ in : %s' % name)

        if len(params) != 0:
            attrs['__params__'] = params
        if len(data) != 0:
            attrs['__data__'] = data
        if len(files) != 0:
            attrs['__files__'] = files
        if len(json) != 0:
            attrs['__json__'] = json
        if len(response) != 0:
            attrs['__response__'] = response
        if len(headers) != 0:
            attrs['__headers__'] = headers
        if len(path) != 0:
            attrs['__path__'] = path
        return type.__new__(cls, name, bases, attrs)


class Model(dict):
    __metaclass__ = ModelMetaclass

    def __init__(self, service=None, params=None, data=None, files=None, json=None, response=None, headers=None,
                 path=None):
        init_kwargs = {}
        for types in (params, data, files, json, response, headers, path):
            if types:
                init_kwargs = dict(init_kwargs, **types)
        # 初步校验传入参数是否在field内,warning
        for ik in init_kwargs.keys():
            for tr in ['__params__', '__data__', '__json__', '__files__', '__headers__', '__path__', '__response__']:
                if hasattr(self, tr) and getattr(self, tr).has_key(ik):
                    break
            else:
                logger.warning("key {} is not found in field,  maybe wrong input! ".format(ik))

        super(Model, self).__init__(**init_kwargs)
        self.run(service)

    def __getattr__(self, item):
        try:
            return self[item]
        except KeyError:
            raise AttributeError(r"'Dict' object has no attribute '%s'" % item)

    def __setattr__(self, key, value):
        self[key] = value

    def run(self, service=None):
        request_info = dict()
        api = getattr(self, '__api__')
        # 如果有path field 替换path中对应的值
        if hasattr(self, '__path__'):
            for k, v in getattr(self, '__path__').items():
                if hasattr(self, k):
                    path_old_key = v.name if v.name else k
                    path_new_value = getattr(self, k)
                    if path_old_key not in api:
                        raise ValueError('key: %s is not found in api: %s' % (path_old_key, api))
                    api = api.replace("/" + str(path_old_key), "/" + str(path_new_value), 1)

        method = getattr(self, '__method__')
        # data headers 获取request info
        for tr in ['__params__', '__data__', '__json__', '__files__', '__headers__']:
            if hasattr(self, tr):
                info = dict()
                for k, v in getattr(self, tr).items():
                    val = getattr(self, k) if hasattr(self, k) else v.default
                    # 外面未传值，而且没有default值，则忽略该入参
                    if val != 'none':
                        if v.name:
                            info[v.name] = val
                        else:
                            info[k] = val
                if tr == '__headers__' and len(info) == 0:
                    pass
                else:
                    request_info[tr.strip('__')] = info
        # 发送请求
        service.http_send(method, api, **request_info)
        if hasattr(self, '__response__'):
            res = getattr(self, '__response__')
            for k, v in res.items():
                arg_name = v.name if v.name else k
                try:
                    actual = getattr(service, arg_name)
                except Exception:
                    actual = "No value found in response!"
                # response_time 验证
                if v.max:
                    msg = u"[%s]性能指标: 实际时间: [%sms] 超过最大值: [%dms]" % (api, service.response_time, v.max)
                    assert_less_equal(service.response_time, v.max, msg)

                # 如果有expect不为None，校验response,Get类型不做检验，需要检验可放在脚本当中
                if method != 'GET':
                    expect = getattr(self, k) if hasattr(self, k) else v.default
                    if expect != 'none':
                        assert_equal(actual, expect,
                                     u"[%s]参数: [%s]-> 实际值: [%s] != 期望值: [%s]" % (api, arg_name, actual, expect))
                else:
                    # Get 情况下 如果外部传了期望值则进行验证，未传的话默认验证status code与default比较
                    if hasattr(self, k):
                        expect = getattr(self, k)
                        assert_equal(actual, expect,
                                     u"[%s]参数: [%s] -> 实际值: [%s] != 期望值: [%s]" % (api, arg_name, actual, expect))
                    elif k == 'status_code':
                        expect = v.default
                        assert_equal(actual, expect,
                                     u"[%s]参数: [status_code]-> 实际值: [%s] != 期望值: [%s]" % (api, actual, expect))

                if actual != "No value found in response!":
                    # 检验结束后保存response
                    setattr(self, k, actual)


class ServiceEntity(object):
    def __init__(self, session=None, hostname=None, verify=False):
        self._entity_flow_from_har = None
        self.hostname = hostname
        if not session:
            self.session = HttpSession(base_url=hostname)
        self._headers = None
        self._cookies = None
        self._auth = None

        self._response = None
        self._json_response = None
        self.verify = verify

    def update_headers(self, k, v):
        if self._headers is None:
            self._headers = {k: v}
        else:
            self._headers.update({k: v})

    @property
    def response(self):
        return self._response

    @property
    def response_time(self):
        return self.session.response_time

    @property
    def status_code(self):
        return self._response.status_code

    @property
    def json_response(self):
        return self._json_response

    def http_send(self, method, api, **kw):
        """
        send http request when request data prepared
        :return:
        """
        # proxies = {
        #     'http': 'http://127.0.0.1:8888',
        #     'https': 'https://127.0.0.1:8888'
        # }
        if self._headers:
            if kw.has_key('headers'):
                kw['headers'].update(self._headers)
            else:
                kw['headers'] = self._headers

        self._response = self.session.request(method=method.lower(), url=self.hostname + api, **kw)
        try:
            self._json_response = self._response.json()
        except:
            pass
        logger.info("{method} {url} {response_time}ms HTTP/1.1 | {req} |{res}".format(method=method,
                                                                                      url=self.hostname + api,
                                                                                      response_time=self.session.response_time,
                                                                                      req=kw.get('data') or kw.get(
                                                                                          'params') or kw.get(
                                                                                          'files'),
                                                                                      res=json.dumps(
                                                                                          self._json_response,
                                                                                          ensure_ascii=False,
                                                                                          encoding='utf-8')))
        if self._json_response and self._json_response.has_key('errors') and len(self._json_response['errors']) == 1:
            logger.debug('error message:%s' % self._json_response['errors'][0])

    def __getattr__(self, attribute):
        if not self._json_response:
            raise Exception("The json response is null.")
        return self.get_item(attribute, self._json_response)

    def get_item(self, attribute, data):
        if '.' in attribute:
            split_char = '.'
        else:
            split_char = '_'
        try:
            attr_list = attribute.split(split_char)
        except ValueError:
            attr_list = [attribute, ]
        result = data
        try:
            for item in attr_list:
                try:
                    item = int(item)
                    result = result[item]
                except ValueError:
                    result = result[item]
        except TypeError:
            raise ValueError("Not found attribute <%s> in data %s" % (attribute, data))
        return result
