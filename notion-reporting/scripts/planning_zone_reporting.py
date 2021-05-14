import sys, os, logging, json
from notion.client import NotionClient
from notion.block import TodoBlock

CONFIG_FILE = "../config.json"
CONFIG = None
LOG_FILE = "../status.log"
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"

def init():
    global CONFIG
    if len(sys.argv) > 2:
        CONFIG_FILE = os.getcwd() + "/" + sys.argv[1] 
        LOG_FILE = os.getcwd() + "/" + sys.argv[2] 

    with open(CONFIG_FILE) as json_file:
        CONFIG = json.load(json_file)
    logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG, format=LOG_FORMAT)
    
def main():
    client = NotionClient(token_v2=CONFIG["token"])
    cv = client.get_collection_view(CONFIG["plan_table"])

    filter_params = {"filters": [{
            "property": "D`kx",
            "filter": {
            "operator": "enum_is_not",
            "value": {
                "type": "exact",
                "value": "下架" 
            }}}
        ],
        "operator": "and"
    }

    result = cv.build_query(filter=filter_params).execute()
    logging.debug("{} Plans found ".format(str(len(result))))

    for row in result:
        logging.debug("Computing " + row.title)
        main_list = []
        main_list = load_children(main_list, row.children)
        row.task_total = len(main_list)
        row.task_completed = len(list(filter(lambda x:x.checked, main_list)))
        logging.debug("Result for {} -> {}/{}".format(row.title, row.task_completed, row.task_total))

def load_children(main_list, children_list):
    for item in children_list:
        if isinstance(item,TodoBlock):
            main_list.append(item)
        
        if len(item.children) > 0:
            load_children(main_list, item.children)

    return main_list

if __name__ == "__main__":
    init()
    main()