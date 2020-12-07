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
    configs["veh_types"] = "https://www.notion.so/c0j0s/d27519769c07444c87a3165ac53e1f50?v=50126105371e4e959b60879354f3379d"
    configs["veh_type_mid"] = "https://www.notion.so/c0j0s/603ea7ccad2847b4a5335ade8ffb7b08?v=7d647975956e49b896285ba8b133c15a"
    configs["camp_route"] = "https://www.notion.so/c0j0s/d8d88e11c1a64fd7bd5047c4fe3ae999?v=cde456130b0948e79882709c6763e4be"
    configs["detail_list"] = "https://www.notion.so/c0j0s/42c45fe6aad64a719ac83d6dd52690a2?v=6fbbce6798f545329e6a9b0932b8367b"
    configs["boc_record"] = "https://www.notion.so/c0j0s/5b319f55357e4c7fbac4ca863addb852?v=5b5aee2bd48d4b6b970f056d02984a82"
    configs["boc"] = "https://www.notion.so/c0j0s/BOC-Template-40002d9de4c3477d8d63725d372f6e7a"
    configs["detail"] = "https://www.notion.so/c0j0s/Detail-Template-ef7205fc9479480083b1d115447d7b20"
    notion = DetailUtils(configs)

if __name__ == "__main__":
    init()
    main()