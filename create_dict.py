import jieba

write_file = open("data/xinchou_dict.txt", "a", encoding='utf8')
read_file = open("data/entity_word.txt", "r", encoding='utf8')
m_list = set()
for i in read_file:
    i = i.split()[0]
    m_list.add(i)

for i in m_list:
    freq = jieba.suggest_freq(i, tune=True)
    write_file.write(i + ' ' + str(freq) + " pro\n")
