

import os
from string import Template

intput_path="input"
output_path="output"

test_path="test"

directory = os.fsencode(intput_path)

def writeFile(filename,chapter):
    filein = open( 'template.xml' )
    src = Template( filein.read() )
    result = src.substitute(chapter)

    fo = open(filename, "w", encoding="utf8")
    print("文件名为: ", fo.name)
    fo.write(result)
    fo.close()
startinx=1007
for file in os.listdir(directory):
     filename = os.fsdecode(file)
     print("reading: " + filename)
     with open(os.path.join(intput_path, filename), encoding="gb2312", errors='ignore') as f:
        chapter = {}
        for line in f:
            if line.startswith('<title>'):
                chapter['title'] = line.replace('<title>',"").replace(',飘天文学</title>','').replace('\n','')
            if line.startswith("<p>"):
                chapter['content'] = line.replace('<p>','　　').replace('<br /><br />','<br/>\n')
        writeFile(output_path + "/chapter"+str(startinx)+".html",chapter)
        startinx += 1

