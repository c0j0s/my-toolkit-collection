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

    def __init__(self, config_file_path, **kwargs):
        self.configs = json.load(open(config_file_path))
        self.client = NotionClient(token_v2=self.configs["token"], **kwargs)

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
        result = self.getTable(table).get_rows(search=keyword)
        if len(result) > 0:
            return result[0]
        else:
            return None

    # create new record: title:mid, type:ref
    def createVehicleMidTypeRecord(self,mid,veh_type):
        # check if vehicle record exists
        veh_ref = self.checkIfRefExists('veh_type_mid',mid)
        if veh_ref is not None:
            return veh_ref

        # check if vehicle type is valid
        veh_type_ref = self.checkIfRefExists('veh_types',veh_type)
        
        if veh_type_ref is None:
            raise Exception("Unknown Vehicle Type")
        else:
            cv = self.getTable('veh_type_mid')
            row = cv.add_row()
            row.icon = '🚙'
            row.mid = mid
            row.vehicle_type_ref = veh_type_ref

            veh_ref = cv.get_rows(search=mid)[0]
        
        return veh_ref

    def createCampRoute(self,aka):
        camp_ref = self.checkIfRefExists('camp_route',aka)
        if camp_ref is not None:
            return camp_ref

        cv = self.getTable('camp_route')
        row = cv.add_row()
        row.icon = '🔃'
        row.name = aka
        row.aka = aka

        camp_ref = cv.get_rows(search=aka)[0]
        return camp_ref

    # get latest Detail Name
    def getLatestDetailIndex(self):
        index = 0
        maxIndex = 0
        cv = self.getTable('detail_list')
        for row in cv.get_rows():
            index = int(row.title.split(" ")[1])
            if index > maxIndex:
                maxIndex = index
        maxIndex += 1
        return maxIndex

    # for creating blocks recursively
    def appendAllBlocks(self,node,template):
        for block in template:
            newNode = node.add_new(block.type,title=block.title)
            if len(block.children) > 0:
                self.appendAllBlocks(newNode.children,block.children)

    # create a now boc record for new detail
    def createBOCRecord(self,detailIndex):
        boc_template = self.getTemplate("boc")
        title = "Detail " + str(detailIndex) + "/1"

        cv = self.getTable('boc_record')
        row = cv.add_row()
        row.icon = '☑️'
        row.title = title
        row.status = boc_template.status
        result = cv.get_rows(search=title)[0]

        path = "https://www.notion.so/c0j0s/" + result.title.replace("/","-") + "-" + result.id.replace("-","")
        page = self.client.get_block(path)
        self.appendAllBlocks(page.children,boc_template.children)
        return result
    
    # create actual detail
    def createDetail(self,detail:Detail):
        detail_template = self.getTemplate("detail")

        cv = self.getTable('detail_list')
        row = cv.add_row()
        row.icon = '🎟️'
        row.title = detail.title
        row.status = detail_template.status
        row.supporting = detail.supporting
        row.purpose = detail.purpose
        row.poc = "[{} ({})](https://wa.me/65{})".format(detail.POC,detail.POCContact,detail.POCContact)

        row.assigned_vehicle = detail.veh_ref
        row.bOC_record = detail.boc_ref
        row.reporting = detail.reporting_ref
        row.destination = detail.destination_ref

        # TODO: duration, reporting,destination
        row.duration = detail.getDuration()

        result = cv.get_rows(search=detail.title)[0]
        return result

    def insertSignInRecord(self,result):
        cv = self.getTable('signin_record')
        row = cv.add_row()
        
        if result["status"]["code"] == 0:
            row.result = str(result["data"]["tips"])
            row.value = int(result["data"]["bellPrize"])
        elif result["status"]["code"] == 30001:
            row.result = str(result["status"]["message"])
            row.value = 0

    def insertDetailToNotion(self,source):
        #remove whatsapp bold
        source = source.replace("*","") 
        if source is "":
            raise Exception("No source provided.")

        # preprocess source, return: detail object
        my_detail = self.preProcessDetail(source)
        result = []

        # check if veh mid record exists, else create record, return: veh mid ref
        for detail in my_detail:
            veh_ref = self.createVehicleMidTypeRecord(detail.mid,detail.vehType)
            reporting_ref = self.createCampRoute(detail.resporting)
            destination_ref_list = []
            for item in detail.destination:
                destination_ref_list.append(self.createCampRoute(item))
            
            # create boc record, return boc record ref
            new_detail_index = self.getLatestDetailIndex()
            boc_ref = self.createBOCRecord(new_detail_index)

            # create detail
            detail.setTitle(new_detail_index)
            detail.setRef(veh_ref,boc_ref,reporting_ref,destination_ref_list)
            detail_ref = self.createDetail(detail)
            result.append(detail_ref)
        
        return result

    def setConfig(self,config_type,key,value):
        self.configs[config_type][key] = value

    def getConfig(self,config_type,key):
        return self.configs[config_type][key]

    def getTable(self,key):
        return self.client.get_collection_view(self.getConfig("Table",key)).collection

    def getTemplate(self,key):
        return self.client.get_block(self.getConfig("Template",key))

    def getProperty(self,key):
        return self.getConfig("Properties",key)