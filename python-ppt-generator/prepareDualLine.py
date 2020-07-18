from langdetect import detect

input = "raw.txt"

finalLines = []
oldLine = ""
oldLang = ""
currentLang = ""
with open(input) as f:
    lines = f.readlines()
    for line in lines:
        if line not in ['\n', '\r\n']:
            currentLang = detect(line)
            if oldLang is not currentLang:
                oldLine = line
                print(line)
                finalLines.append(line.replace("\n",""))
            else: #same language 
                tmp = oldLine.replace("\n","") + " " + line.replace("\n","")
                tmp.replace("  ", "")
                print(tmp)
                del finalLines[-1]
                finalLines.append(tmp)
                oldLine = ""
            oldLang = currentLang
                
with open('combineLine.txt', 'w') as f:
    for item in finalLines:
        f.write("%s\n" % item)
