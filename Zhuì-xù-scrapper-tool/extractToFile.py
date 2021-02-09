import os
import fileinput
import re
import json

intput_path = "input"
output_path = "output"

test_path = "test"
# intput_path = test_path

directory = os.fsencode(intput_path)

master = []
current_ch = {}
for file in os.listdir(directory):
    filename = os.fsdecode(file)
    # print(filename)

    with open(os.path.join(intput_path, filename), encoding="utf8", errors='ignore') as f:
        body = f.read()
        ch = re.findall(r"(?<=<h2>).*(?=</h2>)", body)
        if len(ch) != 0:
            if "title" in current_ch:
                master.append(current_ch)
                current_ch = {}
                print("Chapter added" )
                
            current_ch["title"] = ch[0]
            current_ch["topics"] = []
            print("Reading next chapter: " + ch[0])
        
        topic = {}
        title = re.findall(r"(?<=<h3>).*(?=</h3>)", body)[0]
        topic["title"] = title

        p = re.findall(r"(?<=<p>).*(?=</p>)", body)
        topic["body"] = p

        current_ch["topics"].append(topic)

master.append(current_ch)

with open("master.json","w") as fw:
    fw.write(json.dumps(master, ensure_ascii=False, indent=4))