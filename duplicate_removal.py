if __name__ == '__main__':
    read_file=open("result/final.txt","r",encoding='utf8')
    write_file=open("result/refinal.txt","w",encoding='utf8')
    lines_seen=set()
    count=0;
    for line in read_file:
        if line not in lines_seen:
            count += 1
            write_file.write(line)
            lines_seen.add(line)
    print(count)
    write_file.close()
    print("success")