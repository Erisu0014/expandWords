# import os
# from pyltp import Postagger
# from pyltp import Segmentor
#
# LTP_DATA_DIR = 'D:/python/project/ltpModel/ltp_data_v3.4.0'
# cws_model_path = os.path.join(LTP_DATA_DIR, 'cws.model')
# segmentor = Segmentor()  # 初始化实例
# segmentor.load_with_lexicon(cws_model_path, '../data/xinchou_dict.txt')  # 加载模型，第二个参数是您的外部词典文件路径
# postagger = Postagger()  # 初始化实例
# pos_model_path = os.path.join(LTP_DATA_DIR, 'pos.model')  # 词性标注模型路径，模型名称为`pos.model`
# postagger.load_with_lexicon(pos_model_path, '../data/postagger.txt')  # 加载模型
#
# file = open('../data/entity_word.txt', 'r', encoding='utf8')
# for sequence in file.readlines():
#     words = segmentor.segment(sequence)
#     print(sequence)
#     postags = postagger.postag(words)  # 词性标注
#     print('\t'.join(words).join(postags))
#
# segmentor.release()
# postagger.release()  # 释放模型

