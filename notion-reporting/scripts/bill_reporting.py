import sys, os, logging, json, re
from notion.client import NotionClient

"""
v0.01
"""

def init():
    global CONFIG

    CONFIG_FILE = "../config.json"
    CONFIG = None
    LOG_FILE = "../status.log"
    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"

    if len(sys.argv) > 2:
        CONFIG_FILE = os.getcwd() + "/" + sys.argv[1] 
        LOG_FILE = os.getcwd() + "/" + sys.argv[2] 

    with open(CONFIG_FILE) as json_file:
        CONFIG = json.load(json_file)
    logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG, format=LOG_FORMAT)
    
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
    logging.debug("{} bills found.".format(str(len(result))))

    if len(result) == 0:
        logging.debug("No action needed.")
        return

    try:
        data = []
        for item in result:
            # read raw from notion
            data.append(extractInfo(item.from_email,item.children[0].title))    
            item.recorded = True

        for item in data:
            # write to notion
            filter_params = {
            "operator": "and",
            "filters": [
                {
                "property": "Month",
                "filter": {
                    "operator": "enum_is",
                    "value": {
                    "type": "exact",
                    "value": item["mth"]
                    }
                }
                },
                {
                "property": "Year",
                "filter": {
                    "operator": "enum_is",
                    "value": {
                    "type": "exact",
                    "value": item["year"]
                    }
                }
                }
            ]
            }
            result = bill_record_cv.build_query(filter=filter_params).execute()

            if len(result) > 0:
                logging.debug("Existing bill record found, adding data")
                row = result[0]
                assignInfo(row,item)
            else:
                logging.debug("No bill record found, creating data")
                row = bill_record_cv.collection.add_row()
                row.title = item["year"] + "-" + item["mth"]
                row.year = item["year"]
                row.month = item["mth"]
                row.internet = 29.90
                row.refuse_removal = 8.2497
                assignInfo(row,item)

    except Exception as e:
        logging.error(e)
    finally:
        logging.debug(data)

def extractInfo(biller,source):
    bill = {}

    if biller == "UNION POWER":
        bill["mth"], bill["year"] = re.findall(r"(?<=your ).*(?= Bill)",source)[0].split(" ")
        bill["mth"] = bill["mth"].capitalize() 

        bill["elec"] = re.findall(r"(?<=Usage ).*(?= kWh)",source)[0]
        bill["elec_cost"] = re.findall(r"(?<=\$).*\.[0-9]{2}",source)[0]
        bill["biller"] = "UNION POWER"

    elif biller == "SPPOWER":
        bill["mth"], bill["year"] = re.findall(r"(?<=your ).{8}(?= bill))",source)[0].split(" ")
        bill["mth"] = bill["mth"].capitalize()

        bill["gas_usage"], bill["water_usage"] = re.findall(r"(?<=You)\d*\.\d+|\d+(?= E)",source)
        bill["sp_total"] = re.findall(r"(?<=\$).*\.[0-9]{2}",source)[0]
        bill["biller"] = "SPPOWER"
    
    return bill

def assignInfo(row,bill):
    if bill["biller"] == "UNION POWER":
        row.electricity_usage = int(bill["elec"])
        row.electricity_fee = float(bill["elec_cost"])

    elif bill["biller"] == "SPPOWER":
        row.gas_usage = float(bill["gas_usage"])
        row.water_usage = float(bill["water_usage"])
        row.sp_total = float(bill["sp_total"])
    
    return row

if __name__ == "__main__":
    init()
    logging.debug("Running bill_reporting task.")
    main()
    logging.debug("Exit bill_reporting task.")