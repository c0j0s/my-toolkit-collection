from notion.client import NotionClient 
from notion.collection  import NotionDate 
import json
import re
from datetime import datetime

class Detail(object):
    def setTitle(self, nextDetailIndex):
        self.title = "Detail " + str(nextDetailIndex)

    def setRef(self, veh_ref, boc_ref, reporting_ref = None, destination_ref =None):
        self.veh_ref = veh_ref
        self.boc_ref = boc_ref
        self.reporting_ref = reporting_ref
        self.destination_ref = destination_ref

    def buildFromSource(self,arr):
        for line in arr:
            if line.startswith("Supporting"):
                self.supporting = re.findall(r"(?<=:.)(.*)(?=.for)",line)[0].replace(r"\s",'').replace("\r","")
                self.purpose = re.findall(r"(?<=for.)(.*)(?=)",line)[0].replace("\r","")
            elif line.startswith("Reporting"):
                self.resporting = line.split(": ")[1].replace("\r","")
            elif line.startswith("Destination"):
                self.destination = []

                dest_raw = line.split(": ")[1].replace("\r","")
                if "-" in dest_raw:
                    self.destination = dest_raw.split("-")
                else:
                    self.destination.append(dest_raw)

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
                self.vehType = re.findall(r"(?<=x )(.*)(?=:)",line)[0].upper()
                mid = re.findall(r"(?<=JUNSHENG \()(MID.?[0-9]{5})(?=\))",line)
                if len(mid) == 0:
                    mid = re.findall(r"(?<=JUN SHENG \()(MID.?[0-9]{5})(?=\))",line)
                
                # check again
                if len(mid) == 0:
                    raise Exception("Detail Mid Number Error")
                
                self.mid = mid[0]
                self.mid = self.mid.replace("MID","")
                
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)

    def getDuration(self):
        if self.endDate is "":
            raise Exception("End date is not set")

        if self.startTime is "" or self.endTime is "":
            raise Exception("Start or end time is not set")

        date_format = '%d/%m/%y %H%M'
        startDatetime = self.startDate + " " + self.startTime
        endDatetime = self.endDate + " " + self.endTime
        duration_start = datetime.strptime(startDatetime, date_format)
        duration_end = datetime.strptime(endDatetime, date_format)

        return NotionDate(duration_start,duration_end)

class NotionUtils(object):

    def __init__(self, config_file_path):
        self.configs = json.load(open(config_file_path))
        self.client = NotionClient(token_v2=self.configs["token"])
        self.notion_pages = self.configs["notion_pages"]
        self.notion_templates = self.configs["notion_templates"]
        self.dang = self.configs["dang"]

    def preProcessDetail(self,rawInput):
        myDetail = []
        
        source = rawInput.split("\n")
        singleTmp = []

        detailCount = 1
        currentCount = 0
        for line in source:
            if re.findall(r"^[0-9]{2}(?!\S)",line):
                currentCount = int(line[:2])
                if currentCount < detailCount:
                    detailCount = 1
            else:
                if detailCount == currentCount:
                    singleTmp.append(line)

            if line.startswith("POC"):
                for line in singleTmp:
                    if re.findall(r"JUN.?SHENG",line) or re.findall(r"JUNSHENG",line):
                        x = Detail()
                        x.buildFromSource(singleTmp)
                        myDetail.append(x)
                singleTmp = []
                detailCount += 1
        return myDetail

    def checkIfRefExists(self,table,keyword):
        cv = self.client.get_collection_view(table)
        result = cv.collection.get_rows(search=keyword)
        if len(result) > 0:
            return result[0]
        else:
            return None

    # create new record: title:mid, type:ref
    def createVehicleMidTypeRecord(self,mid,veh_type):
        # check if vehicle record exists
        veh_ref = self.checkIfRefExists(self.notion_pages['veh_type_mid'],mid)
        if veh_ref is not None:
            return veh_ref

        # check if vehicle type is valid
        veh_type_ref = self.checkIfRefExists(self.notion_pages['veh_types'],veh_type)
        
        if veh_type_ref is None:
            raise Exception("Unknown Vehicle Type")
        else:
            cv = self.client.get_collection_view(self.notion_pages['veh_type_mid'])
            row = cv.collection.add_row()
            row.icon = '🚙'
            row.mid = mid
            row.vehicle_type_ref = veh_type_ref

            veh_ref = cv.collection.get_rows(search=mid)[0]
        
        return veh_ref

    def createCampRoute(self,aka):
        camp_ref = self.checkIfRefExists(self.notion_pages['camp_route'],aka)
        if camp_ref is not None:
            return camp_ref

        cv = self.client.get_collection_view(self.notion_pages['camp_route'])
        row = cv.collection.add_row()
        row.icon = '🔃'
        row.name = aka
        row.aka = aka

        camp_ref = cv.collection.get_rows(search=aka)[0]
        return camp_ref

    # get latest Detail Name
    def getLatestDetailIndex(self):
        index = 0
        maxIndex = 0
        cv = self.client.get_collection_view(self.notion_pages['detail_list'])
        for row in cv.collection.get_rows():
            index = int(row.title.split(" ")[1])
            if index > maxIndex:
                maxIndex = index
        maxIndex += 1
        return maxIndex

    # for getting template content
    def getTemplate(self,path):
        return self.client.get_block(path)

    # for creating blocks recursively
    def appendAllBlocks(self,node,template):
        for block in template:
            newNode = node.add_new(block.type,title=block.title)
            if len(block.children) > 0:
                self.appendAllBlocks(newNode.children,block.children)

    # create a now boc record for new detail
    def createBOCRecord(self,detailIndex):
        boc_template = self.getTemplate(self.notion_templates["boc"])
        title = "Detail " + str(detailIndex) + "/1"

        cv = self.client.get_collection_view(self.notion_pages['boc_record'])
        row = cv.collection.add_row()
        row.icon = '☑️'
        row.title = title
        row.status = boc_template.status
        result = cv.collection.get_rows(search=title)[0]

        path = "https://www.notion.so/c0j0s/" + result.title.replace("/","-") + "-" + result.id.replace("-","")
        page = self.client.get_block(path)
        self.appendAllBlocks(page.children,boc_template.children)
        return result
    
    # create actual detail
    def createDetail(self,detail:Detail):
        detail_template = self.getTemplate(self.notion_templates["detail"])

        cv = self.client.get_collection_view(self.notion_pages['detail_list'])
        row = cv.collection.add_row()
        row.icon = '🎟️'
        row.title = detail.title
        row.status = detail_template.status
        row.supporting = detail.supporting
        row.purpose = detail.purpose
        row.poc = detail.POC
        row.poc_contact_no = int(detail.POCContact)

        row.assigned_vehicle = detail.veh_ref
        row.bOC_record = detail.boc_ref
        row.reporting = detail.reporting_ref
        row.destination = detail.destination_ref

        # TODO: duration, reporting,destination
        row.duration = detail.getDuration()

        result = cv.collection.get_rows(search=detail.title)[0]
        return result

    def insertSignInRecord(self,result):
        cv = self.client.get_collection_view(self.notion_pages['signin_record'])
        row = cv.collection.add_row()
        if int(result["status"]["code"]) == 30001:
            row.value = 0
        else:  
            row.value = 5

        row.result = result

    # def updateBookReadingProgress(self,result):
