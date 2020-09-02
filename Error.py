# -*- coding: utf-8 -*-

import time

from Constant import init_data


class HmError(Exception):
    def __init__(self, code=0, message=''):
        self.code = code
        self.message = message
        super(HmError, self).__init__()

    def __str__(self):
        return "代码:%d 信息:%s" % (self.code, self.message)


class OperateException(Exception):
    def __init__(self, message=''):
        self.message = message
        super(OperateException, self).__init__()

    def __str__(self):
        return "操作错误:" + self.message

    def __repr__(self):
        return "操作错误:" + self.message


def error_find(data, url=''):
    if 'eid' in data:
        if int(data['eid']) == -1:
            time.sleep(3)            
        if int(data['eid']) in init_data.error_code:
            raise HmError(code=data['eid'],
                          message="错误代码:" + str(data['eid']) + "  " + init_data.error_code[int(data['eid'])]+'--url '+url)
        else:
            raise HmError(
                code=data['eid'], message="未知错误:%d 请等待修复" % data["eid"]+'--url '+url)
