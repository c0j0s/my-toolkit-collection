import os
import re
import shutil
import fileinput

def inplace_change(filename, old_string, new_string):
    # Safely read the input filename using 'with'
    with open(filename) as f:
        s = f.read()
        if old_string not in s:
            print('"{old_string}" not found in {filename}.'.format(**locals()))
            return

    # Safely write the changed content, if found in the file
    with open(filename, 'w') as f:
        print('Changing "{old_string}" to "{new_string}" in {filename}'.format(**locals()))
        s = s.replace(old_string, new_string)
        f.write(s)

# intput_path="test"
intput_path="input"
output_path="output"

directory = os.fsencode(intput_path)
filesToRename = []
count = 0
for file in os.listdir(directory):
    filename = os.fsdecode(file)
    with open(intput_path + "/" + filename, 'r') as f:
        fb = f.read()
        # matches = re.findall(r"(?<=<h3>).*(?=</h3>)", fb)
        matches = re.findall(r"(?<=<title>).*(?=</title>)", fb)
        
        if len(matches) == 1:            
            title = matches[0].split(" ")[0]
            ori_title = matches[0]
            title_matches = re.findall(title, fb)
            if len(title_matches) != 2:
                print("error: {} | {} --> {}".format(filename,title, str(len(title_matches))))
                
                inplace_change(intput_path + "/" + filename, title, "")
                inplace_change(intput_path + "/" + filename, "<title></title>", "<title>{}</title>".format(ori_title))
                inplace_change(intput_path + "/" + filename, "<h3></h3>","<h3>{}</h3>".format(ori_title))

