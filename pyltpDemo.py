from pyltp import SentenceSplitter
sentenceSplitter=SentenceSplitter.split('基本薪酬的制度执行')
print('\n'.join(sentenceSplitter))

import os
LTP_DATA_DIR='D:/python/project/ltpModel/ltp_data_v3.4.0'
cws_model_path=os.path.join(LTP_DATA_DIR,'cws.model')

# from pyltp import Segmentor
# segmentor=Segmentor()
# segmentor.load(cws_model_path)
# words=segmentor.segment('不可预料的风险在当代具有很高的现实意义')
# print(' '.join(words))
# segmentor.release()

from pyltp import Segmentor
segmentor = Segmentor()  # 初始化实例
segmentor.load_with_lexicon(cws_model_path, 'data/xinchou_dict.txt') # 加载模型，第二个参数是您的外部词典文件路径
words = segmentor.segment('基本薪酬的制度执行')
print ('\t '.join(words))
segmentor.release()

from pyltp import Postagger
postagger = Postagger() # 初始化实例
pos_model_path = os.path.join(LTP_DATA_DIR, 'pos.model')  # 词性标注模型路径，模型名称为`pos.model`
postagger.load_with_lexicon(pos_model_path,'data/postagger.txt')  # 加载模型
postags = postagger.postag(words)  # 词性标注
print ('\t'.join(postags))
postagger.release()  # 释放模型

# #命名实体识别
# from pyltp import NamedEntityRecognizer
# ner_model_path = os.path.join(LTP_DATA_DIR, 'ner.model')
# recognizer = NamedEntityRecognizer() # 初始化实例
# recognizer.load(ner_model_path)  # 加载模型
# netags = recognizer.recognize(words, postags)  # 命名实体识别
# print ('\t'.join(netags))
# recognizer.release()  # 释放模型


par_model_path = os.path.join(LTP_DATA_DIR, 'parser.model')  # 依存句法分析模型路径，模型名称为`parser.model`
from pyltp import Parser
parser = Parser() # 初始化实例
parser.load(par_model_path)  # 加载模型
arcs = parser.parse(words, postags)  # 句法分析
print ("\t".join((str(arc.head)+':'+arc.relation) for arc in arcs))
parser.release()  # 释放模型