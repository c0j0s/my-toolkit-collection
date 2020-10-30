import os
import re
import shutil

# intput_path="test"
intput_path="input"
output_path="output"

directory = os.fsencode(intput_path)
filesToRename = []
count = 0
for file in os.listdir(directory):
    filename = os.fsdecode(file)
    with open(intput_path + "/" + filename, 'r') as f:
        matches = re.findall(r"(?<=<h3>).*(?=</h3>)", f.read())
        # matches = re.findall(r"(?<=<title>).*(?=</title>)", f.read())
        
        newFilename = filename
    
        if str(matches[0]).startswith(" "):
            if len(matches) == 1:            
                newFilename = "{:04d}".format(count) + ". 第X章" + matches[0].replace("'","").replace("（","(").replace("）",")").replace("？","?").replace("！","!").replace("、",", ") + ".xhtml"

            print("Rename: {} --> {}".format(filename, newFilename))
            shutil.copy(intput_path + "/" + filename, output_path + "/" + newFilename)
    count += 1
    
