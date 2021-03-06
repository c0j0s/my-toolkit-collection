from datetime import datetime
import sys, os, logging, json, re
from notion.client import NotionClient
from notion.collection import NotionDate

"""
v0.04
"""

def init():
    global CONFIG

    CONFIG_FILE = "../config.json"
    CONFIG = None
    LOG_FILE = "../logs/error.log"
    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"

    if len(sys.argv) > 2:
        CONFIG_FILE = os.getcwd() + "/" + sys.argv[1] 
        LOG_FILE = os.getcwd() + "/" + sys.argv[2] 

    with open(CONFIG_FILE) as json_file:
        CONFIG = json.load(json_file)
    logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format=LOG_FORMAT)
    
def main():
    client = NotionClient(token_v2=CONFIG["token"])
    bill_record_cv = client.get_collection_view(CONFIG["bill_record_table"])
    bill_raw_cv = client.get_collection_view(CONFIG["bill_raw_table"])

    filter_params = {
        "operator": "and",
        "filters": [
            {
            "property": "Recorded",
            "filter": {
                "operator": "checkbox_is",
                "value": {
                "type": "exact",
                "value": False
                }
            }
            }
        ]
        }

    result = bill_raw_cv.build_query(filter=filter_params).execute()
    logging.info("{} bills found.".format(str(len(result))))

    if len(result) == 0:
        logging.info("No action needed.")
        return

    for item in result:
        # read each raw bills sent from email
        try:
            bill = extractInfo(item.from_email,item.children[0].title)

            filter_params = {
            "operator": "and",
            "filters": [
                {
                "property": "Month",
                "filter": {
                    "operator": "enum_is",
                    "value": {
                    "type": "exact",
                    "value": bill["mth"]
                    }
                }
                },
                {
                "property": "Year",
                "filter": {
                    "operator": "enum_is",
                    "value": {
                    "type": "exact",
                    "value": bill["year"]
                    }
                }
                }
            ]
            }

            # query for existing row in bill record with same month and year
            result = bill_record_cv.build_query(filter=filter_params).execute()

            if len(result) > 0:
                logging.info("Existing bill record found, adding data")
                row = result[0]
            else:
                logging.info("No bill record found, creating a new row data")
                row = bill_record_cv.collection.add_row()
                row.title = bill["year"] + "-" + bill["mth"]
                row.year = bill["year"]
                row.month = bill["mth"]
                row.internet = 29.90
                row.refuse_removal = 8.2497

            # assign other common attributes
            assignInfo(row,bill)

            # mark as completed
            item.recorded = True
            item.recorded_on = NotionDate(datetime.now())
        except Exception as e:
            # mark as completed
            item.recorded = False
            logging.error(e, " at main")

def extractInfo(biller,source):
    
    bill = {}
    bill["mth"], bill["year"] = re.findall(r"(?<=[Y|y]our ).{8,9}(?= e?[B|b]ill)",source)[0].split(" ")
    bill["mth"] = bill["mth"][:3].capitalize()

    if biller == "collection@unionpower.com.sg":
        bill["elec"] = re.findall(r"(?<=Usage ).*(?= kWh)",source)[0]
        bill["elec_cost"] = re.findall(r"(?<=\$).*\.[0-9]{2}",source)[0]
        

    elif biller == "ebillsummary@spgroup.com.sg":
        bill["water_usage"], bill["gas_usage"] = re.findall(r"(?<=You)\d*\.?\d+|\d+(?= E)",source)
        bill["sp_total"] = re.findall(r"(?<=\$).*\.[0-9]{2}",source)[0]
    
    elif biller == "ebill@m1.com.sg":
        bill["internet"] = re.findall(r"(?<=\$).*\.[0-9]{2}",source)[0]

    else:
        logging.error([biller,source])
        raise Exception("Unable to identify biller at extractInfo.")

    bill["biller"]=biller
    return bill

def assignInfo(row,bill):
    if bill["biller"] == "collection@unionpower.com.sg":
        row.electricity_usage = int(bill["elec"])
        row.electricity_fee = float(bill["elec_cost"])

    elif bill["biller"] == "ebillsummary@spgroup.com.sg":
        row.gas_usage = float(bill["gas_usage"])
        row.water_usage = float(bill["water_usage"])
        row.sp_total = float(bill["sp_total"])
    
    elif bill["biller"] == "ebill@m1.com.sg":
        row.internet = float(bill["internet"])
        pass
    else:
        logging.error([row,bill])
        raise Exception("Unable to assign bill info to notion row at assignInfo.")

    return row

if __name__ == "__main__":
    init()
    logging.info("Running bill_reporting task.")
    main()
    logging.info("Exit bill_reporting task.")