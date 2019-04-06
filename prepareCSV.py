input = "combineLine.txt"

with open(input) as f:
    while True:
        line1 = f.readline().replace("\n","")
        line2 = f.readline().replace("\n","")
        print('"'+line1 +'","'+line2+'"')
        if not line2: break