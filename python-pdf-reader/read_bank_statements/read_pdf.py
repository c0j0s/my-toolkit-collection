import pdfreader
from pdfreader import PDFDocument, SimplePDFViewer
import re
import tabula
import json
import sys

translate = {
    "FAST Payment / Receipt".lower():["ICT","Credit"],
    "Salary".lower():["SAL","Credit"],
    "Debit Card Transaction".lower():["MST","Debit"],
    "Point-of-Sale Transaction or Proceeds".lower():["POS","Debit"],
    "Point-of-Sale Transaction".lower():["POS","Debit"],
    "Cash Withdrawal".lower(): ["AWL","Debit"],
    "Cash Deposit Machine".lower(): ["CAM","Credit"],
    "Payments / Collections via GIRO".lower():["IBG","Credit"],
    "Interest Earned".lower():["INT","Credit"],
    "Funds Transfer".lower():["ITR","Debit"],
    "Monthly Savings Amount for MySavings/POSB SAYE Account".lower():["MCO","Debit"],
    "Unit Trust Application".lower():["UTA","Debit"],
    "S$Fixed Deposit Placement".lower():["FD","Debit"],
    "Top-up ".lower():["SHUB","Debit"],
    "Remittance Transfer of Funds".lower():["RTF","Credit"],
    "D2P".lower():["D2P","Debit"],
    "Quick Cheque Deposit".lower():["QCD","Credit"]
}

file_name = sys.argv[1]

fd = open(file_name, "rb")
doc = SimplePDFViewer(fd)

extracted_raw = []
count = 1
skip = 0
while True:
    try:
        doc.navigate(count)
        doc.render()

        read = False

        page_data = doc.canvas.strings
        for line in page_data:
            if skip == 0:
                if read and line != " ":
                    extracted_raw.append(re.sub(' +', ' ', line))
            else:
                skip -= 1

            if line == "Balance Brought Forward":
                read = True
                skip = 1
            elif line == "Balance Carried Forward":
                read = False
                skip = 1
                del extracted_raw[-1]
            elif line == "Total":
                skip = 2
                del extracted_raw[-1]
        count += 1
    except:
        break

with open(file_name.replace("data","output").replace(".pdf","_raw.json"),"w") as f:
    f.write(json.dumps(extracted_raw,indent=4))
    f.close()

is_entry = False
next_entry = False
entry_tmp = []
entry_list = []
for idx, line in enumerate(extracted_raw):
    if re.match(r"[0-9]{2} [A-z]{3}",line):
        if not is_entry:
            is_entry = True
        else:
            next_entry = True
        
    if next_entry or idx == len(extracted_raw) - 1:
        entry_list.append(entry_tmp)
        entry_tmp = []
        next_entry = False

    if is_entry:
        entry_tmp.append(line)

with open(file_name.replace("data","output").replace(".pdf",".json"),"w") as f:
    f.write(json.dumps(entry_list,indent=4))
    f.close()

class Entry:
    Transaction_Date = ""
    Reference = ""
    Debit_Amount = ""
    Credit_Amount = ""
    Transaction_Ref1 = ""
    Transaction_Ref2 = ""
    Transaction_Ref3 = ""

entry_object_list = []
entry_no_ref_code = []
ref_code_not_found = False
for item in entry_list:
    e = Entry()
    e.Transaction_Date = item[0].replace(" ","-") + "-" + file_name[7:9]

    values = []
    for amt in item:
        if re.match(r"[0-9]*\,?[0-9]{0,3}\.[0-9]{2}",amt):
            values.append(amt)

    if item[1] == "Monthly ":
        item[1] = "Monthly Savings Amount for MySavings/POSB SAYE Account"

    if item[1].lower() in translate:
        e.Reference = translate[item[1].lower()][0]
        if translate[item[1].lower()][1] == "Debit":
            e.Debit_Amount = values[0]
        else:
            e.Credit_Amount = values[0]
        ref_code_not_found = False
    else:
        ref_code_not_found = True

    
    if not ref_code_not_found:
        for v in values:
            item.remove(v)

        if len(item) > 3:
            other_info = item[1:-1]
            e.Transaction_Ref1 = other_info[0]
            e.Transaction_Ref3 = other_info[-1]

            other_info.remove(e.Transaction_Ref1)
            other_info.remove(e.Transaction_Ref3)
            
            e.Transaction_Ref2 = ' '.join(other_info)
        else:
            e.Transaction_Ref1 = ' '.join(item[0:-1])

        entry_object_list.append(e)
    else:
        entry_no_ref_code.append(item)

if len(entry_no_ref_code) > 0:
    print(str(entry_no_ref_code))

with open(file_name.replace("data","output").replace(".pdf",".csv"),"w") as f:
    not_written = []
    f.write("Transaction Date,Reference,Debit Amount,Credit Amount,Transaction Ref1,Transaction Ref2,Transaction Ref3\n")
    for item in entry_object_list:
        if item.Credit_Amount == "0.00" or item.Debit_Amount == "0.00":
            not_written.append(item)
        else:
            line = '"{}","{}","{}","{}","{}","{}","{}"\n'.format(item.Transaction_Date,item.Reference,item.Debit_Amount,item.Credit_Amount,item.Transaction_Ref1,item.Transaction_Ref2,item.Transaction_Ref3)
        f.write(line)
    f.close()

    if len(not_written) > 0:
        print("Not Written:") 
        print(json.dumps([ob.__dict__ for ob in not_written]))

