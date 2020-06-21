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
            elif re.findall(r"(?=JUN.?SHENG \()(.*)(?=\))",line):
                self.vehType = re.findall(r"(?<=x )(.*)(?=:)",line)[0]
                self.mid = re.findall(r"(?<=JUNSHENG \()(MID[0-9]{5})(?=\))",line)[0]
                if len(self.mid) == 0:
                    self.mid = re.findall(r"(?<=JUN SHENG \()(MID[0-9]{5})(?=\))",line)[0]
                
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)

def preProcessDetail(rawInput):
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
                if re.findall(r"JUN.?SHENG",line):
                    myDetail.append(singleTmp)
            singleTmp = []
            detailCount =+ 1
    return myDetail

x = """
The following are details from 220620-280620

Monday 22 June

01
1x AOUV: LCP WEI LONG (MID33581)
Supporting: HQ 2SIB for BDE ATP STORE RUN
22/06/20 1000hrs to 22/06/20 2000hrs
Reporting: MHC
Destination: PLC
POC: 2WO NG BUCK TEO (91282541)

02
1x SOUV: LCP FATTAH (MID34149)
Supporting: 16C4I for 12KM Route March
22/06/20 1800hrs to 22/06/20 2200hrs
Reporting: MHC
Destination: MHC
POC: CPT ZHANG XIN (91685596)
____________

Tuesday 23 June

01
1x SOUV: LCP JUNSHENG (MID34131)
Supporting: 16C4I for IPPT RSTA JUNE
23/06/20 0600hrs to 23/06/20 0900hrs
Reporting: MHC
Destination: MHC
POC: 3SG NICHOLAS (93281558)
_____________

Wednesday 24 June

01
1x SOUV: LCP SHENGHUA (MID34131)
Supporting: 2SIR for IPPT (CHARLIE)
24/06/20 0500hrs to 24/06/20 1030hrs
Reporting: KC3
Destination: KC3
POC: 2WO LIN ZHIXIANG VICTOR (81895015)

02
1x AOUV: PTE TAARIQ (MID34130)
Supporting: 2SIR for CQB Live Firing (Alpha)
24/06/20 0430hrs to 24/06/20 2359hrs
Reporting: KC3
Destination: MMRC/PLC
POC: 3WO MUHAMMAD ASHIK (98259454)

03
1x F550: LCP THILAN (MID34811)
Supporting: 16C4I for 12KM Route March
24/06/20 1800hrs to 24/06/20 2200hrs
Reporting: MHC
Destination: MHC
POC: LTA JAVIN CHEN (90890459)

04
1x SOUV: LCP LOKE WEI LONG (MID34149)
Supporting: 16C4I SIG COY IPPT 
24/06/20 0600hrs to 24/06/20 0930hrs
Reporting: MHC
Destination: MHC
POC: 2LT JAVIN (90890459)
_____________

Thursday 25 June

01
1x SOUV: LCP ROSMAWIE (MID34131)
Supporting: 16C4I for IPPT RSTA JUNE
25/06/20 0600hrs to 25/06/20 0900hrs
Reporting: MHC
Destination: MHC
POC: 3SG NICHOLAS (93281558)

02
1x AOUV: LCP FATTAH (MID34128)
Supporting: 2SIR for CQB LIVE FIRING (BRAVO)
25/06/20 0530hrs to 25/06/20 2200hrs
Reporting: KC3
Destination: MMRC/PLAD
POC: 3WO CHOY MUN KIT (86872200)

03
1x SOUV: LCP WEI LONG (MID34149)
Supporting: 2SIR for IPPT (SUPPORT)
25/06/20 0530hrs to 25/06/20 1030hrs
Reporting: KC3
Destination: KC3
POC: 3WO XIE WEIYOU (98295697)
_____________

Friday 26 June

01
1x SOUV: LCP JUNSHENG (MID34131)
Supporting: 2SIR for OFFICER UIP SKILL AT ARMS (SUPPORT)
26/06/20 1530hrs to 26/06/20 2130hrs
Reporting: KC3
Destination: KC3
POC: 3WO XIE WEIYOU (98295697)

02
1x SOUV: LCP THILAN (MID34149)
Supporting: 2SIR for IPPT (ALPHA)
26/06/20 0500hrs to 26/06/20 1030hrs
Reporting: KC3
Destination: KC3
POC: 3WO MUHAMMAD ASHIK (98259454)

03
1x OUV: LCP PANG CHI KIT (MID33581)
1x F550: LCP LUO QI ZHONG (MID34804)
26/06/20 1530hrs to 26/06/20 2359hrs
Supporting: 16C4I 12km ROUTE MARCH 
Reporting:  MHC
Destination: LORONG ASARAMA TRG 
POC: 3SG NICHOLAS (93281558)

_____________

Saturday 27 June

01
1x SOUV: LCP FATTAH (MID34149)
1x AOUV: PTE TAARIQ (MID34146)
1x 5TON GS: LCP JIAN MING (MID20988)
27/06/20 0000hrs to 28/06/20 2359hrs
Supporting: 16C4I for NAVAX EX
Reporting: MHC
Destination: MHC
POC: 2SG ANDY NG (94599822)
_____________

Sunday 28 June

01
1x SOUV: LCP CHI KIT (MID34131)
1x 5TON GS: LCP JIA LU (MID21232)
Supporting: 2SIR for ATP (M) CHARLIE
28/06/20 0400hrs to 29/06/20 2359hrs
Reporting: KC3
Destination SAFTI 300M RANGE
POC: 2WO LIN ZHIXIANG VICTOR (81895015)
"""

ds = preProcessDetail(x)
for item in ds:
    x = Detail()
    x.buildFromSource(item)
    print(x.toJSON())