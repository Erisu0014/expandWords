#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@Time    : 2018/11/26 16:02
@Author  : Erisu-
@contact: guoyu01988@163.com
@File    : Node.py
@Software: PyCharm
@Desc:  节点类
'''


class Node:
    inputMap = dict()
    outputMap = dict()
    part = ""

    def __init__(self, word):
        self.word = word
        self._i = 0

    def input_update(self, key, value):
        if key in self.inputMap.keys():
            temp_set = self.inputMap[key]
            temp_set.add(value)
        else:
            temp_set = set()
            temp_set.add(value)
            self.inputMap[key] = temp_set

    def output_update(self, key, value):
        if key in self.inputMap.keys():
            temp_set = self.outputMap[key]
            temp_set.add(value)
        else:
            temp_set = set()
            temp_set.add(value)
            self.outputMap[key] = temp_set

    def __iter__(self):
        return Node(self.word + ':' + self.part + '\n inputMap:' + self.inputMap + '\n outputMap:' + self.outputMap)
