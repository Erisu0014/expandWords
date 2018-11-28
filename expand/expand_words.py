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
import re
import sys as sys
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
candidate = set()  # 候选词，候选词中的词是待扩展的词
# right_tags = set(("ATT", "ADV"))
right_tags = set(("ADT",))
left_tags = set(("RAD", "COO"))
before_expend = []  # 前置扩展栈
all_words = set()


# 或许我们根本不需要词的后置扩展，因为我们甚至不知道自己扩展的是什么词
# after_expend = []  # 后置扩展栈


def initialize(entity_file):
    warnings.filterwarnings('ignore')
    for word in entity_file.readlines():
        entity_words.add(word.strip())
    return "success"


def sentence_split(read_file):
    for paragraph in read_file.readlines():
        # print(paragraph)
        sentence_splitter = SentenceSplitter.split(paragraph)
        # 此处分出的词有标点，(还要进行二次整理的过程?)
        # 必须进行二次整理，我服了
        # print('\n'.join(sentence_splitter))
        for sequence in sentence_splitter:
            # 去除空行
            if sequence == '':
                continue
            second_sentences = re.split('(；|，)', sequence)
            for second_sentence in second_sentences:
                if len(second_sentence.strip()) == 1:
                    continue
                # print(second_sentence)
                sequences.add(second_sentence)
    return "success"


def words_split():
    count = 1  # 用以记录当前的循环过程
    segmentor = Segmentor()
    cws_model_path = os.path.join(LTP_DATA_DIR, 'cws.model')
    segmentor.load_with_lexicon(cws_model_path, '../data/xinchou_dict.txt')
    for sequence in sequences:
        words = segmentor.segment(sequence)
        # print('\t '.join(words))
        # 进行结构化存储
        index = 1
        for word in words:
            node = Node(word, index)
            nodes.append(node)
            index = index + 1
        # 进行词性标注工作
        postags = words_postagger(words)
        # 进行词句法分析工作
        parsing(words, postags)
        # 对句子中是否存在entity_words进行判断
        if has_entity(sequence):
            # 进行词扩展
            temp_words = words_expanding()
            # print(temp_words)
            # 判断其是否是entity_words的扩充词
            temp_words = is_expanded(temp_words)
            print('step' + str(count) + ':' + '\t'.join(temp_words))
            count = count + 1
            for temp_word in temp_words:
                all_words.add(temp_word)
                # nodes全部删除，候选词全部删除
        nodes.clear()
        candidate.clear()
    segmentor.release()

    return "success"


def words_postagger(words):
    postagger = Postagger()
    pos_model_path = os.path.join(LTP_DATA_DIR, 'pos.model')  # 词性标注模型路径，模型名称为`pos.model`
    postagger.load_with_lexicon(pos_model_path, 'data/postagger.txt')  # 加载模型
    postags = postagger.postag(words)
    for (node, postag) in zip(nodes, postags):
        node.part = postag
    postagger.release()

    return postags


# 句法分析工作与结构化存储
def parsing(words, postages):
    par_model_path = os.path.join(LTP_DATA_DIR, 'parser.model')  # 依存句法分析模型路径，模型名称为`parser.model`
    parser = Parser()
    parser.load(par_model_path)
    arcs = parser.parse(words, postages)
    # print("\t".join((str(arc.head) + ':' + arc.relation) for arc in arcs))
    # for i in range(len(nodes)):
    #     nodes[i].output_update(arcs[i].relation, nodes[arcs[i].head])
    #     nodes[arcs[i].head].input_update(arcs[i].relation, nodes[i])
    for (node, arc) in zip(nodes, arcs):
        # ATT,ADV同等看待
        if arc.relation == 'ADV' or arc.relation == 'ATT':
            node.output_update('ADT', nodes[arc.head - 1])
            nodes[arc.head - 1].input_update('ADT', node)
        else:
            node.output_update(arc.relation, nodes[arc.head - 1])
            nodes[arc.head - 1].input_update(arc.relation, node)
    # 结构化结束，打印输出
    # for node in nodes:
    #     node.print_self()
    parser.release()


# 判断一个句子中是否存在entity_word，且知道这个句子将要扩展的扩展词是什么
def has_entity(sequence):
    boolean = False
    for word in entity_words:
        if word in sequence:
            boolean = True
            candidate.add(word)
    return boolean


# 词扩展
def words_expanding():
    max_words = list()
    for node in nodes:
        for key, values in node.inputMap.items():
            if key in right_tags:
                for value in reversed(values):
                    track_expand(value)
        # 单词实现了words_expending
        prefix = ''
        while len(before_expend) > 0:
            prefix = prefix + before_expend.pop()
        # 前缀拼接
        # print('prefix=' + prefix)
        if prefix is '':
            continue
        prefix = prefix + node.word
        # 判断是否前缀已经在max_words中出现过了
        boolean = False
        for max_word in max_words:
            if max_word.find(prefix) != -1:
                boolean = True
                break
            # 双向比较
            if prefix.find(max_word) != -1:
                max_words.remove(max_word)
                break
        if boolean is False:
            max_words.append(prefix)
    return max_words


# 递归扩展与补充
def track_expand(node):
    # 右向填充
    for keys, values in node.inputMap.items():
        if keys in left_tags:
            # COO可能会有多个
            for value in reversed(values):
                before_expend.append(value.word)
            break

    before_expend.append(node.word)
    # 左向填充
    for keys, values in node.inputMap.items():
        if keys in right_tags:
            # 可能会有多修饰的情况，反序遍历压栈
            for value in reversed(values):
                # before_expend.append(value.word)
                track_expand(value)

    return before_expend


# 判断是否为扩展词的扩展
def is_expanded(words):
    final_words = list()
    for word in words:
        for candy in candidate:
            if word.find(candy) != -1:
                final_words.append(word)
                break
    return final_words


def write_files():
    file = open('../data2/expend_words.txt', 'w', encoding='utf8')
    for word in all_words:
        file.write(word + "\n")


if __name__ == '__main__':
    entity_file = open('../data/entity_word.txt', 'r', encoding='utf8')
    # 初始化操作
    initialize(entity_file)
    read_file = open('../book/txt001.xhtml.txt', 'r', encoding='utf8')
    # 句子抽取
    sentence_split(read_file)
    # 分词
    words_split()
    # 文件写入
    write_files()
