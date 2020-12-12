import json
import re

class Detail:
    """
    Detail object class, methods to interact with detail data.
    v0.01
    """

    reporting_ref = None
    veh_ref = None
    destination_ref = None
    boc_ref = None

    def __init__(self,is_subject="",veh_type="",mid="",supporting="",purpose="",start_date="",start_time="",end_date="",end_time="",reporting="",destination="",poc_contact="",poc=""):
        self.is_subject = is_subject
        self.veh_type = veh_type
        self.mid  = mid
        self.supporting  = supporting
        self.purpose  = purpose
        self.start_date  = start_date
        self.start_time  = start_time
        self.end_date  = end_date
        self.end_time  = end_time
        self.reporting  = reporting
        self.destination = destination
        self.poc  = poc
        self.poc_contact  = poc_contact

    def build_detail_objects_from_list(self, source:list, person:str="JUNSHENG",debug=False):
        """
        Converts list of detail text into an detail object.
        source: detail text list
        """
        for line in source:
            s = line.split(":")

            if len(s) > 1:
                # Other line
                initial = s[0]
                content = s[1]

                if initial == "Reporting":
                    self.reporting = content.lstrip()
                elif initial == "Destination":
                    self.destination = content.lstrip()
                elif initial == "POC":
                    self.poc = re.search(r"(?<=: )(.*)(?=\s?\([0-9])", line)[0]
                    self.poc_contact = re.search(r"[0-9]{8}", line)[0]
                elif initial == "Supporting":
                    x = []
                    if "for" in content:
                        x = content.split(" for ")
                    else:
                        x = content.split(" ")
                    self.supporting = x[0].lstrip()
                    self.purpose = " ".join(x[1:]).lstrip()
                else:
                    if person in content:
                        self.is_subject = True

                        vt = re.search(r"(?<=x ).*", initial)
                        assert vt is not None, "Unable to cast vehicle type string"

                        self.veh_type = vt[0].upper()
                        for i in content.split(", "):
                            if person in i:
                                mid = re.search(r"(?<=\(MID)[0-9]{5}(?=\))", i)
                                assert mid is not None, "Unable to cast MID string"

                                self.mid = mid[0]
                    else:
                        self.mid = ""
                        self.veh_type = ""
                        self.is_subject = False
            else:
                # Duration line
                dates = re.findall(r"..\/..\/..", line)
                hrs = re.findall(r"[0-9]{4}(?=hrs)", line)
                assert len(dates) > 1 and len(hrs) > 1, "Unable to cast duration string"

                self.start_date = dates[0]
                self.start_time = hrs[0]
                self.end_date = dates[1]
                self.end_time = hrs[1]
           
    """
    Helper functions
    """

    def to_json(self):
        """
        Converts detail object to JSON string.
        """
        return json.dumps(self.__dict__, indent=4)


