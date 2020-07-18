from NotionWrapper import Detail, NotionWrapper

notion = NotionWrapper("./config.json")
detail_collection = notion.get_table("detail_list")

for row in detail_collection.get_rows():
    row.poc = "[{} ({})](https://wa.me/65{})".format(row.poc,
                                                     row.poc_contact_no, row.poc_contact_no)
    print(row.poc)
