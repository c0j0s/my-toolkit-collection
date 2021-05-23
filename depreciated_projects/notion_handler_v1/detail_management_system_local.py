import traceback
from detail_util import *

DEBUG = True

source="""
"""

def main():
    try:
        print("Detail Task Handler Started")
        result = notion.insert_detail_to_notion(source,debug=DEBUG)

        if DEBUG:
            print(result[0].to_json())
        else:
            print(result)

    except Exception as e:
        print(traceback.format_exc())
    except KeyboardInterrupt as e:
        exit()


def init():
    global notion, configs
    configs = {}
    configs["token"]=""
    configs["veh_types"] = "<REMOVED>"
    configs["veh_type_mid"] = "<REMOVED>"
    configs["camp_route"] = "<REMOVED>"
    configs["detail_list"] = "<REMOVED>"
    configs["boc_record"] = "<REMOVED>"
    configs["boc"] = "<REMOVED>"
    configs["detail"] = "<REMOVED>"
    notion = DetailUtils(configs)

if __name__ == "__main__":
    init()
    main()