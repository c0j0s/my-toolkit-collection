input_data = {'moduleCode': 'CS1010J'}

"""
Start of Zapier Script Body (v0.01)
"""
import requests, datetime
output = {}

if len(input_data) <= 0:
    output['debug'] = "Invalid input data."
else:
    output['moduleCode'] = str(input_data['moduleCode']).upper()

    if output['moduleCode'] == '' or output['moduleCode'] == None:
        output['debug'] = "Invalid module code."
    else:
        api = "https://api.nusmods.com/v2/2021-2022/modules/{}.json".format(output['moduleCode'])
        print(api)

        response = requests.get(api)

        if response.status_code == 200:
            output = response.json()

            output['availableSem'] = [
                "SEM1" if 'mpes1' in output['attributes'] and output['attributes']['mpes1'] else '',
                "SEM2" if 'mpes2' in output['attributes'] and output['attributes']['mpes2'] else ''
            ]
            output['su'] = output['attributes']['su'] if 'su' in output['attributes'] else False

            output['exams'] = []
            for item in output['semesterData']:
                if 'examDate' in item:
                    output['exams'].append('Date:{} Dur:{}Min'.format(item['examDate'],item['examDuration']))

            del output['attributes']
            del output['semesterData']
        else:
            output['debug'] = response.status_code

output['last_update'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
"""
End of Zapier Script Body
"""
print(output)