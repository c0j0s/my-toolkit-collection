from flask import Flask, request, jsonify
from notionUtils import Detail, NotionWrapper
from dangdangUtils import DangDangUtils
import time
import atexit
import traceback

from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
notionUtil = NotionWrapper("./config.json")
dangdangUtil = DangDangUtils(notionUtil.dang['dang_endpoint'],notionUtil.dang['token'])

@app.route('/')
def home():
    response = jsonify({"status":"alive"})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response 

@app.route('/getDetailTemplate/<detail>')
def getDetailTemplate(detail):
    data = {}
    msg = ""
    detail_ref = notionUtil.check_if_ref_exists(notionUtil.notion_pages['detail_list'] ,detail)
    if detail_ref == None:
        data = ""
        msg = "No Detail Found"
    else:
        data['veh_mid'] = detail_ref.assigned_vehicle[0].mid
        data['veh_type'] = detail_ref.assigned_vehicle[0].vehicle_type_ref[0].title
        data['veh_avi'] = detail_ref.boc_record[0].fe
        data['veh_fe'] = detail_ref.boc_record[0].avi
        data['poc'] = detail_ref.poc
        data['poc_contact_no'] = detail_ref.poc_contact_no
    response = jsonify({"status":"Success","data":data,"msg":msg})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response 

@app.route('/insert_detail_to_notion/', methods=['POST'])
def insert_detail_to_notion():
    result = {
            "status":"",
            "detail":[]
    }
    try:
        #remove whatsapp bold
        source = str(request.data.decode('UTF-8')).replace("*","") 

        if source == "":
            raise Exception("No source provided.")
        
        # preprocess source, return: detail object
        my_detail = notionUtil.pre_process_detail(source)

        # check if veh mid record exists, else create record, return: veh mid ref
        for detail in my_detail:
            veh_ref = notionUtil.create_vehicle_md_type_record(detail.mid,detail.vehType)
            reporting_ref = notionUtil.create_camp_route(detail.resporting)
            destination_ref_list = []
            for item in detail.destination:
                destination_ref_list.append(notionUtil.create_camp_route(item))
            

            # create boc record, return boc record ref
            new_detail_index = notionUtil.get_latest_detail_index()
            boc_ref = notionUtil.create_boc_record(new_detail_index)

            # create detail
            detail.set_title(new_detail_index)
            detail.set_ref(veh_ref,boc_ref,reporting_ref,destination_ref_list)
            detail_ref = notionUtil.create_detail(detail)
            result["detail"].append([detail_ref.id,detail_ref.title])
        
        result["status"] = "Success"
    except Exception as e:
        traceback.print_tb(e.__traceback__)
        result["status"] = str(e)

    print(result)
    response = jsonify(result)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/daily_sign_in/')
def daily_sign_in():
    notionUtil.insert_sign_in_record(dangdangUtil.daily_sign_in())
    return "Done"

cron = BackgroundScheduler(daemon=True)
# Explicitly kick off the background thread

cron.add_job(daily_sign_in,'interval',hours=24)
cron.start()

atexit.register(lambda: cron.shutdown(wait=False))

if __name__ == "__main__":
    app.debug = True 
    # app.run(host='127.0.0.1', port=5000)
    app.run(host='0.0.0.0', port=5000)
