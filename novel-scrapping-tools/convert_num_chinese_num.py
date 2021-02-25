

import itertools
import os
from string import Template
import fileinput
import re

intput_path = "input"
output_path = "output"

test_path = "test"


def replaceName(filename, old_title, new_title):
    fin = open(filename, "rt", encoding='utf8')
    # read file contents to string
    data = fin.read()
    # replace all occurrences of the required string
    data = data.replace(old_title, new_title)
    # close the input file
    fin.close()
    # open the input file in write mode
    fin = open(filename, "wt", encoding='utf8')
    # overrite the input file with the resulting data
    fin.write(data)
    # close the file
    fin.close()


def renameFile(filename):
    newName = filename.replace('chapter', 'extra')
    print(filename+" => " + newName)
    os.rename(filename, newName)


def num2chinese(num, big=False, simp=True, o=False, twoalt=False):
    """
    Converts numbers to Chinese representations.
    `big`   : use financial characters.
    `simp`  : use simplified characters instead of traditional characters.
    `o`     : use 〇 for zero.
    `twoalt`: use 两/兩 for two when appropriate.
    Note that `o` and `twoalt` is ignored when `big` is used, 
    and `twoalt` is ignored when `o` is used for formal representations.
    """
    # check num first
    nd = str(num)
    if abs(float(nd)) >= 1e48:
        raise ValueError('number out of range')
    elif 'e' in nd:
        raise ValueError('scientific notation is not supported')
    c_symbol = '正负点' if simp else '正負點'
    if o:  # formal
        twoalt = False
    if big:
        c_basic = '零壹贰叁肆伍陆柒捌玖' if simp else '零壹貳參肆伍陸柒捌玖'
        c_unit1 = '拾佰仟'
        c_twoalt = '贰' if simp else '貳'
    else:
        c_basic = '〇一二三四五六七八九' if o else '零一二三四五六七八九'
        c_unit1 = '十百千'
        if twoalt:
            c_twoalt = '两' if simp else '兩'
        else:
            c_twoalt = '二'
    c_unit2 = '万亿兆京垓秭穰沟涧正载' if simp else '萬億兆京垓秭穰溝澗正載'

    def revuniq(l): return ''.join(
        k for k, g in itertools.groupby(reversed(l)))
    nd = str(num)
    result = []
    if nd[0] == '+':
        result.append(c_symbol[0])
    elif nd[0] == '-':
        result.append(c_symbol[1])
    if '.' in nd:
        integer, remainder = nd.lstrip('+-').split('.')
    else:
        integer, remainder = nd.lstrip('+-'), None
    if int(integer):
        splitted = [integer[max(i - 4, 0):i]
                    for i in range(len(integer), 0, -4)]
        intresult = []
        for nu, unit in enumerate(splitted):
            # special cases
            if int(unit) == 0:  # 0000
                intresult.append(c_basic[0])
                continue
            elif nu > 0 and int(unit) == 2:  # 0002
                intresult.append(c_twoalt + c_unit2[nu - 1])
                continue
            ulist = []
            unit = unit.zfill(4)
            for nc, ch in enumerate(reversed(unit)):
                if ch == '0':
                    if ulist:  # ???0
                        ulist.append(c_basic[0])
                elif nc == 0:
                    ulist.append(c_basic[int(ch)])
                elif nc == 1 and ch == '1' and unit[1] == '0':
                    # special case for tens
                    # edit the 'elif' if you don't like
                    # 十四, 三千零十四, 三千三百一十四
                    ulist.append(c_unit1[0])
                elif nc > 1 and ch == '2':
                    ulist.append(c_twoalt + c_unit1[nc - 1])
                else:
                    ulist.append(c_basic[int(ch)] + c_unit1[nc - 1])
            ustr = revuniq(ulist)
            if nu == 0:
                intresult.append(ustr)
            else:
                intresult.append(ustr + c_unit2[nu - 1])
        result.append(revuniq(intresult).strip(c_basic[0]))
    else:
        result.append(c_basic[0])
    if remainder:
        result.append(c_symbol[2])
        result.append(''.join(c_basic[int(ch)] for ch in remainder))
    return ''.join(result)


directory = os.fsencode(intput_path)
for file in os.listdir(directory):
    filename = os.fsdecode(file)
    index = int(filename.split(" ")[0].replace(".", ""))
    chinese_index = num2chinese(index, o=False)
    
    if index > 100:
        chinese_index = num2chinese(index, o=True)
        chinese_index = chinese_index.replace("零", "〇").replace("百", "")

        if chinese_index.endswith("十"):
            chinese_index = chinese_index.replace("十", "〇")
        else:
            chinese_index = chinese_index.replace("十", "")

    newName = filename.replace("X", chinese_index)
    print(newName)
    os.rename(intput_path + "/" + filename,intput_path + "/" + newName)

    s,h,t,n = "","","",""

    with open(intput_path + "/" + newName) as f:
        s = f.read()
        h = re.findall(r"<h3>.*</h3>", s)[0]
        t = re.findall(r"<title>.*</title>", s)[0]
        n = newName.split(".")[1][1::]
        print(n)
        
    with open(intput_path + "/" + newName, 'w') as f:
        s = s.replace(h, "<h3>{}</h3>".format(n))
        s = s.replace(t, "<title>{}</title>".format(n))
        f.write(s)
