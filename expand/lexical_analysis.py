#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@Time    : 2018/11/28 18:58
@Author  : Erisu-
@contact: guoyu01988@163.com
@File    : lexical_analysis.py
@Software: PyCharm
@Desc: 词法分析，对文件中的词进行一筛和二筛
'''
import os
from pyltp import Segmentor
from pyltp import Postagger

LTP_DATA_DIR = 'D:/python/project/ltpModel/ltp_data_v3.4.0'
cws_model_path = os.path.join(LTP_DATA_DIR, 'cws.model')


def screen():
    expand_file = open('../data2/expend_words.txt', 'r', encoding='utf8')
    expand_words = list()
    for str in expand_file.readline():
        expand_words.append(str)
    expanded_file = open('../data2/final_words.txt', 'w', encoding='utf8')

    # segmentor = Segmentor()
    # cws_model_path = os.path.join(LTP_DATA_DIR, 'cws.model')
    # segmentor.load_with_lexicon(cws_model_path, '../data/xinchou_dict.txt')
    # for expand_word in expand_words:
    #     words = segmentor.segment(expand_word)
    #     for word in words:
