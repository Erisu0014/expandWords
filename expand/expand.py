#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@Time    : 2018/11/26 14:32
@Author  : Erisu-
@contact: guoyu01988@163.com
@File    : expand.py
@Software: PyCharm
@Desc: 词扩展
'''
import os
import warnings

from pyltp import SentenceSplitter
from pyltp import Segmentor
from pyltp import Postagger
from pyltp import Parser

from expand.Node import Node

LTP_DATA_DIR = 'D:/python/project/ltpModel/ltp_data_v3.4.0'  # ltp路径
entity_words = set()  # 用以后续词扩展的初始词
sequences = set()  # 分离出的句子组
# Nodes的暂存数据在我们对一句话的所有分词进行分析结束后就会清空
nodes = list()  # 分离出的词


def initialize(entity_file):
    warnings.filterwarnings('ignore')
    for word in entity_file.readlines():
        entity_words.add(word.strip())
    return "success"


def sentence_split(read_file):
    for paragraph in read_file.readlines():
        print(paragraph)
        sentence_splitter = SentenceSplitter.split(paragraph)
        # 此处分出的词有标点，(还要进行二次整理的过程?)
        print('\n'.join(sentence_splitter))
        for sequence in sentence_splitter:
            sequences.add(sequence)
    return "success"


def words_split():
    segmentor = Segmentor()
    cws_model_path = os.path.join(LTP_DATA_DIR, 'cws.model')
    segmentor.load_with_lexicon(cws_model_path, '../data/xinchou_dict.txt')
    for sequence in sequences:
        words = segmentor.segment(sequence)
        # print('\t '.join(words))
        # 进行结构化存储
        for word in words:
            node = Node(word)
            nodes.append(node)
        # 进行词性标注工作
        postags = words_postagger(words)
        # 进行词句法分析工作
        words_expanding()
    segmentor.release(words, postags)

    return "success"


def words_postagger(words):
    postagger = Postagger()
    pos_model_path = os.path.join(LTP_DATA_DIR, 'pos.model')  # 词性标注模型路径，模型名称为`pos.model`
    postagger.load_with_lexicon(pos_model_path, 'data/postagger.txt')  # 加载模型
    postags = postagger.postag(words)
    for postag, node in postags, nodes:
        node.part = postag
    return postags


# 句法分析工作与结构化存储
def parsing(words, postages):
    par_model_path = os.path.join(LTP_DATA_DIR, 'parser.model')  # 依存句法分析模型路径，模型名称为`parser.model`
    parser = Parser()
    parser.load(par_model_path)
    arcs = parser.parse(words, postages)
    for arc, node in arcs, nodes:
        node.output_update(arc.relation, nodes[arc.head])
        nodes[arc.head].input_update(arc.relation, node)
    # 结构化结束，打印输出
    for node in nodes:
        print(node)


def words_expanding():
    pass


def words_filter():
    pass


def write_files():
    pass


if __name__ == '__main__':
    entity_file = open('../data/entity_word.txt', 'r', encoding='utf8')
    # 初始化操作
    initialize(entity_file)
    read_file = open('../book/test.txt', 'r', encoding='utf8')
    # 句子抽取
    sentence_split(read_file)
    # 分词
    words_split()
    # 词扩展
    words_expanding()
    # 词筛选
    words_filter()
    # 文件写入
    write_files()
