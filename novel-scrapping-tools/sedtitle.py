

import os
from string import Template
import fileinput


intput_path="input"
output_path="output"

test_path="test"


# def writeFile(filename,chapter):
#     filein = open( 'template.xml' )
#     src = Template( filein.read() )
#     result = src.substitute(chapter)
#     print(result)

#     #fo = open(filename, "w", encoding="utf8")
#     #print("文件名为: ", fo.name)
#     #fo.write(result)
#     #fo.close()
    
def replaceName(filename,old_title,new_title):
    fin = open(filename, "rt", encoding='utf8')
    #read file contents to string
    data = fin.read()
    #replace all occurrences of the required string
    data = data.replace(old_title, new_title)
    #close the input file
    fin.close()
    #open the input file in write mode
    fin = open(filename, "wt", encoding='utf8')
    #overrite the input file with the resulting data
    fin.write(data)
    #close the file
    fin.close()

def renameFile(filename):
    newName = filename.replace('chapter','extra')
    print( filename+" => " + newName)
    os.rename(filename,newName)

chapters = []
with open('toc.txt',encoding="utf8") as t:
    for line in t:
        chapters.append(line.split('_')[1].replace("\n",""))


directory = os.fsencode(intput_path)
filesToRename = []
for file in os.listdir(directory):
    filename = os.fsdecode(file)

    if filename.startswith("extra"):
        continue

    with open(os.path.join(intput_path, filename), encoding="utf8", errors='ignore') as f:
        chapter = {}
        for line in f:
            if line.startswith('  <title>'):
                old_title = line.replace('  <title>',"").replace('</title>','').replace("\n","")
                
                if("章" not in old_title):
                    print(old_title)
                    # filesToRename.append(os.path.join(intput_path, filename))

      
for item in filesToRename:
    renameFile(item)


