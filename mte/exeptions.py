# coding: utf-8

class MyBaseError(BaseException):
    pass


class ParamsError(MyBaseError):
    pass


class ResponseError(MyBaseError):
    pass


class ParseResponseError(MyBaseError):
    pass


class ValidationError(MyBaseError):
    pass


class FunctionNotFound(NameError):
    pass


class VariableNotFound(NameError):
    pass


class ApiNotFound(NameError):
    pass


class SuiteNotFound(NameError):
    pass
