import json
import re

class Detail(object):
    def buildFromSource(self,arr):
        for line in arr:
            if line.startswith("Supporting"):
                self.supporting = re.findall(r"(?=:)(.*)(?=for)",line)[0].replace(r"\s",'')
                self.purpose = re.findall(r"(?<=for.)(.*)(?=)",line)[0]
            elif line.startswith("Reporting"):
                self.resporting = line.split(": ")[1]
            elif line.startswith("Destination"):
                self.destination = line.split(": ")[1]
            elif line.startswith("POC"):
                self.POC = re.findall(r"(?<=: )(.*)(?= \([0-9])",line)[0]
                self.POCContact = re.findall(r"[0-9]{8}",line)[0]
            elif re.findall(r"..\/..\/..",line):
                dates,hrs = ["",""]

                dates = re.findall(r"..\/..\/..",line)
                hrs = re.findall(r"[0-9]{4}(?=hrs)",line)
                self.startDate = dates[0]
                self.startTime = hrs[0]
                self.endDate = dates[1]
                self.endTime = hrs[1]
            elif re.findall(r"(?=<REMOVED>.?<REMOVED> \()(.*)(?=\))",line):
                self.vehType = re.findall(r"(?<=x )(.*)(?=:)",line)[0]
                self.mid = re.findall(r"(?<=<REMOVED> \()(MID[0-9]{5})(?=\))",line)[0]
                if len(self.mid) == 0:
                    self.mid = re.findall(r"(?<=<REMOVED> <REMOVED> \()(MID[0-9]{5})(?=\))",line)[0]
                
    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)

def pre_process_detail(rawInput):
    myDetail = []
    
    source = rawInput.split("\n")
    singleTmp = []

    detailCount = 1
    currentCount = 0
    for line in source:
        if re.findall(r"^[0-9]{2}(?!\S)",line):
            currentCount = int(line)
            if currentCount < detailCount:
                detailCount = 1
        else:
            if detailCount == currentCount:
                singleTmp.append(line)

        if line.startswith("POC"):
            for line in singleTmp:
                if re.findall(r"<REMOVED>.?<REMOVED>",line):
                    myDetail.append(singleTmp)
            singleTmp = []
            detailCount =+ 1
    return myDetail

x = """
<REMOVED>
"""

ds = pre_process_detail(x)
for item in ds:
    x = Detail()
    x.buildFromSource(item)
    print(x.to_json())