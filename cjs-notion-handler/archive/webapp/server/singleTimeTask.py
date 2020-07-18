from notionUtils import Detail, NotionWrapper

notionUtil = NotionWrapper("./config.json")
detail_collection = notionUtil.getTable("detail_list")
# https://wa.me/6598295697

for row in detail_collection.collection.get_rows():
    row.poc = "[{} ({})](https://wa.me/65{})".format(row.poc,row.poc_contact_no,row.poc_contact_no)
    print(row.poc)