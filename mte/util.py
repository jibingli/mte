# coding:utf-8

import datetime
import json
import os
import random
from datetime import date
from datetime import timedelta

from mte.finallogger import logger

ARR = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
LAST = ('1', '0', 'x', '9', '8', '7', '6', '5', '4', '3', '2')

PATH = lambda p: os.path.abspath(
    os.path.join(os.path.dirname(__file__), p)
)
districtcode_path = PATH('./districtcode.txt')
d = datetime.datetime.now()


def get_random_phonenumber(self):
    logger.debug("Begin to generate phone number...")
    number = random.choice(['133', '151', '187', '170']) + "".join(random.choice("0123456789") for i in range(8))
    logger.debug("phone number: %s" % str(number))
    return number


def intersection_of_path(self, file_path):
    """
    拼接绝对路径的文件路径,方便文件的读取
    :param file_path: 有单一相交路径的相对路径
    :return: 拼接完成的绝对路径
    """
    relative_file_path = os.path.normpath(file_path)
    relative_list = relative_file_path.split(os.sep)
    sys_path_now_list = os.path.dirname(__file__).split(os.sep)[1:]
    for i in xrange(len(sys_path_now_list)):
        if (relative_list[0] == sys_path_now_list[i]):
            intersection = i
    prepose_path = ''.join(['/%s' % y for y in sys_path_now_list[:intersection]])
    return os.path.join(prepose_path, file_path)


def _getDistrictCode(self):
    with open(districtcode_path, "rb") as file:
        data = file.read()

    district_list = data.split('\n')
    code_list = []
    for node in district_list:
        # print node
        if node[10:11] != ' ':
            state = node[10:].strip()
        if node[10:11] == ' ' and node[12:13] != ' ':
            city = node[12:].strip()
        if node[10:11] == ' ' and node[12:13] == ' ':
            district = node[14:].strip()
            code = node[0:6]
            code_list.append(
                {"state": state, "city": city, "district": district, "code": code})
    return code_list

    # 生成身份证号


def create_realname_and_id_number(self):
    # real_name = random.choice(['Test', 'test', 'user', 'random']) + "".join(
    #     random.choice("0123456789") for i in range(3))
    real_name = random.choice(['赵', '钱', '孙', '李']) + "".join(
        random.choice(['随', '机', '生', '成', '中', '文', '姓', '名']) for i in range(2))
    logger.debug("generate id number:")
    '''生成身份证号'''
    code_list = self._getDistrictCode()
    id = code_list[random.randint(0, len(code_list))]['code']  # 地区项
    id = id + str(random.randint(1930, 2013))  # 年份项
    da = date.today() + timedelta(days=random.randint(1, 366))  # 月份和日期项
    id = id + da.strftime('%m%d')
    id = id + str(random.randint(100, 999))  # ，顺序号简单处理

    i = 0
    count = 0
    weight = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]  # 权重项
    checkcode = {'0': '1', '1': '0', '2': 'X', '3': '9', '4': '8',
                 '5': '7', '6': '6', '7': '5', '8': '5', '9': '3', '10': '2'}  # 校验码映射
    for i in range(0, len(id)):
        count = count + int(id[i]) * weight[i]
    id = id + checkcode[str(count % 11)]  # 算出校验码
    logger.debug("realName is %s and ID is %s" % (real_name, id))
    return real_name, id


def generate_bank_card_number(self):
    # 622588： 招商银行借记卡 621226: 工商
    bank_card = random.choice(['62122653']) + "".join(random.choice("0123456789") for i in range(11))
    # bank_card_split = ' '.join([bank_card[i:i + 4] for i in range(0, len(bank_card), 4)])
    # logger.debug("Bank Card No.: %s" % bank_card_split)
    return bank_card


def now_time(self):
    now = datetime.datetime.now()
    strdatetime = now.strftime("%Y%m%d%H%M%S")
    return strdatetime


def string_to_dict(self, s):
    import ast
    result = ast.literal_eval(s)
    return result


def dict_to_string(self, d):
    return json.dumps(d)
