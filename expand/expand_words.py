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
right_tags = set(("ATT",))
left_tags = set(("RAD", "COO"))
before_expend = []  # 前置扩展栈
all_words = set()
min_order = 1000
right_part = ['n', 'nh', 'ni', 'nl', 'ns', 'nt', 'nz', 'v', 'm']
# wrong_part_adj = ['r', 'm', 'p']
wrong_part_first = ['r', 'q', 'p', 'u', 'm', 'nd']
# 词反转
reverse_word_e = {'》': '《', '”': '“'}
reverse_word_b = {'《': '》', '“': '”'}


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
            second_sentences = re.split('[:.（）、\s]', sequence)
            for second_sentence in second_sentences:
                sequences.add(second_sentence)
    #         second_sentences = re.split('(；|，|、|）|\.|\n|\?|？|！|\!|》|。)', sequence)
    #         new_sents = []
    #         # 分隔后是['第一章\u3000薪酬管理总论', '\n'的形式，所以要/2调整
    #         for i in range(int(len(second_sentences) / 2)):
    #             sent = second_sentences[2 * i] + second_sentences[2 * i + 1]
    #             # print(sent)
    #             new_sents.append(sent)
    #         # 去空行
    #         for li in new_sents:
    #             if "\n" in li:
    #                 for i in li.split("\n"):
    #                     if len(li.strip()) <= 4:
    #                         continue
    #                     sequences.add(i)
    #             else:
    #                 if len(li.strip()) <= 4:
    #                     continue
    #                 sequences.add(li)
    #         new_sents = []
    # print(sequences)


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
            temp_words = words_expanding_2()
            # print(temp_words)
            # 判断其是否是entity_words的扩充词
            temp_words = is_expanded(temp_words)
            # 判断temp_words两边是否有符号（主要针对的是”“）
            # 此处有bug，对于“xxxx”“aaaa”的形式无法判断
            # 对temp_words中每一个word都进行判断
            index = 0
            for word in temp_words:
                if word[0] == '“' and word[-1] == '”':
                    word = word[1:]
                    word = word[:-1]
                temp_words[index] = word
                index = index + 1
            index = 0
            print('step' + str(count) + ':' + '\t'.join(temp_words))
            count = count + 1
            for temp_word in temp_words:
                all_words.add(temp_word)
        # nodes全部删除，候选词全部删除
        nodes.clear()
        candidate.clear()
    # sequences清空
    sequences.clear()
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
        # if arc.relation == 'ADV' or arc.relation == 'ATT':
        #     node.output_update('ADT', nodes[arc.head - 1])
        #     nodes[arc.head - 1].input_update('ADT', node)
        # else:
        #     node.output_update(arc.relation, nodes[arc.head - 1])
        #     nodes[arc.head - 1].input_update(arc.relation, node)
        # 增加限制，对于非修饰性词汇不将其放入到关系组中
        # if node.part in wrong_part_adj and arc.relation is 'ATT':
        #     continue
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


# 词扩展方法1
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


def words_expanding_2():
    max_words = list()
    global min_order
    for node in nodes:
        if node.part not in right_part:
            continue
        for key, values in node.inputMap.items():
            if key in right_tags:
                # 方法2
                for value in values:
                    min_order = track_expend_2(value)
                    min_order = min(int(min_order), value.order)
        # 单词实现了words_expending
        prefix = ''
        # 通过flag_bool确保只有一次头舍
        flag_bool = False
        if int(min_order) < node.order:
            for num in range(min_order, node.order):
                if flag_bool is False:
                    if nodes[num - 1].part in wrong_part_first or nodes[num - 1].word == '—':
                        continue
                    else:
                        flag_bool = True
                prefix = prefix + nodes[num - 1].word
            # 判断是否需要在词头添加信息,未进行是否为词前后符号的判断
            if min_order >= 2:
                temp_word = nodes[min_order - 2].word
                if temp_word in reverse_word_b:
                    # 可能要加入数量判断
                    if prefix.find(reverse_word_b[temp_word]) != -1:
                        prefix = nodes[min_order - 2].word + prefix
        min_order = 1000
        # 前缀拼接
        # print('prefix=' + prefix)
        if prefix is '':
            continue
        prefix = prefix + node.word
        # 判断是否需要在词尾加入符号
        for key, values in node.inputMap.items():
            if key == 'WP':
                if len(values) > 1:
                    # 双引号会有多个指向，注意
                    for value in values:
                        # 词尾
                        if value.word in reverse_word_e.keys():
                            temp_value = reverse_word_e[value.word]
                        else:
                            temp_value = value.word
                        if value.order == node.order + 1 and prefix.find(temp_value) != -1:
                            prefix = prefix + value.word
                            break

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


def track_expend_2(node):
    global min_order
    # 只要找到最左边的ADT就压栈并遍历
    for key, values in node.inputMap.items():
        if key in right_tags:
            for value in values:
                min_order = track_expend_2(value)
                min_order = min(int(min_order), value.order)
    return min_order


# 判断是否为扩展词的扩展
# 如果只是符号扩展那么没有任何意义
def is_expanded(words):
    final_words = list()
    for word in words:
        for candy in candidate:
            word_temp = word.replace('“', '').replace('”', '')
            if word_temp.find(candy) != -1 and candy != word_temp:
                if (len(word) - len(candy)) > 7:
                    continue
                final_words.append(word)
                break
    return final_words


def write_files():
    file = open('../data2/expend_words.txt', 'w', encoding='utf8')
    for word in all_words:
        file.write(word + "\n")


def listdir(path, list_name):  # 传入存储的list
    for file in os.listdir(path):
        file_path = os.path.join(path, file)
        if os.path.isdir(file_path):
            listdir(file_path, list_name)
        else:
            list_name.append(file_path)


if __name__ == '__main__':
    entity_file = open('../data/entity_word.txt', 'r', encoding='utf8')
    # 初始化操作
    initialize(entity_file)
    # 文件夹下读取待扩展的文件路径
    bookList = list()
    listdir("D:/python/project/jiebademo/book", bookList)
    for i in range(len(bookList)):
        read_file = open(bookList[i], "r", encoding='utf-8')
        # 句子抽取
        sentence_split(read_file)
        # 分词
        words_split()

    # 文件写入
    # write_files()
