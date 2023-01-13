out = open("cmdList.txt",'w')
inf = open("cmdList_single.txt",'r')
count = 0
for line in inf:
    count += 1
    out.write(line.strip())
    if count%5 == 0: out.write('\n')
    else: out.write('NEWLINE')

