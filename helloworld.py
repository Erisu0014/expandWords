# _*_coding:utf-8_*_
import jieba
import jieba.posseg as pseg
import re
import os

# 标注数组
labelL = ['n', 'nz', 'an', 'nt']
labelB = ['n', 'nz', 'an', 'nt', 'a', 'shi', 'vn']
label_Track = ['n', 'nz', 'an', 'nt', 'uj', 'shi', 'j', 'vn', 'eng', 'b', 'pro']
wrong_words = ['大量', '经验', '部分', '特色', '一流', '问题', '花费', '主要', '位会员', '记录', '方面']


def backtrack(st, i):
    # print('res_list=' + str(st))

    return ""


def listdir(path, list_name):  # 传入存储的list
    for file in os.listdir(path):
        file_path = os.path.join(path, file)
        if os.path.isdir(file_path):
          listdir(file_path, list_name)
        else:
          list_name.append(file_path)


def labeltrack(flags, words, i):
    tempstr = words[i]
    begin = i
    # print(tempstr)
    # 引入新规则，count记录,如果v之后是vn，则将其加入扩展组中
    if i >= 1 and flags[i - 1] == 'uj':
        tempstr = words[i - 1] + tempstr
        i = i - 1
        # or (flags[i - 1] == 'v' and flags[i]=='vn')
        while i >= 1 and (flags[i - 1] in label_Track or (flags[i - 1] == 'v' and flags[i] == 'vn')):
            tempstr = words[i - 1] + tempstr
            i = i - 1

    if (begin != i and i >= 1 and flags[i] == 'uj'):
        tempstr = tempstr[1::]
    while (begin != i and i >= 1 and words[i] in wrong_words):
        tempstr = tempstr[len(words[i])::]
        i = i + 1
        if (i >= 1 and flags[i] == 'uj'):
            tempstr = tempstr[1::]
    return tempstr


if __name__ == '__main__':
    # 实体词，用以之后的比较与扩展
    entity_file = open("data/entity_word.txt", "r", encoding='utf8')
    entity = set()
    for i in entity_file:
        i = i.strip()
        entity.add(i)
    entity_file.close()
    jieba.load_userdict("data/xinchou_dict.txt")  # 加载用户自定义词典
    #print(entity)
    # 写入suggest防止切割
    #print("*" * 20)

    # 定义写入文件
    write_file = open("result/final.txt", "w", encoding='utf8')

    res_list = []

    #文件夹下读取相应文件并输出
    resultList=list()
    listdir("D:\\python\\project\\jiebademo\\result",resultList)

    # 读入文件并分词
    for i in range(1, len(resultList)):
        #f = open("book/txt00" + str(i) + ".xhtml.txt", "r", encoding='utf-8')
        f = open(resultList[i], "r", encoding='utf-8')
        paragraph = "".join([m for m in f.readlines() if m.strip()])
        sentences = re.split('(。|！|\!|？|,|\?|\n)', paragraph)
        new_sents = []
        # 分隔后是['第一章\u3000薪酬管理总论', '\n'的形式，所以要/2调整
        for i in range(int(len(sentences) / 2)):
            sent = sentences[2 * i] + sentences[2 * i + 1]
            # print(sent)
            new_sents.append(sent)
        my_sents = []
        # 去空行
        for li in new_sents:
            if "\n" in li:
                for i in li.split("\n"):
                    my_sents.append(i)
            else:
                my_sents.append(li)
        # 名词合并
        for ju in my_sents:
            fen = pseg.cut(ju.strip())
            words = []
            flags = []
            index = 0  # 循环计数
            for word, flag in fen:
                if index > 1:
                    if flag in labelL and flags[index - 1] in labelB:
                        words[index - 1] = words[index - 1] + word
                        continue
                words.append(word)
                flags.append(flag)
                index += 1
            # print('words='+str(words))
            # print('flags='+str(flags))
            # 向前检索补充
            if (words == ['']):
                continue
            # print('res_list=' + str(res_list))
            # print("=" * 20)
            for i in range(0, len(words)):
                if words[i] in entity:
                    # print(flags[i]+','+words[i])
                    midstr = labeltrack(flags, words, i)
                    if (midstr != words[i]):
                        res_list.append(midstr)
                        # print(midstr)
            # write_file.write()
    print("=" * 20)
    print(res_list)
    for i in res_list:
        write_file.write(i + "\n")
