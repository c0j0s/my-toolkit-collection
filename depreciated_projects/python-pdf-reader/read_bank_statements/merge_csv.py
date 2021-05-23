
files = ['201601.csv', '201602.csv', '201603.csv', '201604.csv', '201605.csv', '201606.csv', '201607.csv', '201608.csv', '201609.csv', '201610.csv', '201611.csv', '201612.csv', '201701.csv', '201702.csv', '201703.csv', '201704.csv', '201705.csv', '201706.csv', '201707.csv', '201708.csv', '201709.csv', '201710.csv', '201711.csv', '201712.csv',
         '201801.csv', '201802.csv', '201803.csv', '201804.csv', '201805.csv', '201806.csv', '201807.csv', '201808.csv', '201809.csv', '201810.csv', '201811.csv', '201812.csv', '201901.csv', '201902.csv', '201903.csv', '201904.csv', '201905.csv', '201906.csv', '201907.csv', '201908.csv', '201909.csv', '201910.csv', '201911.csv', '201912.csv', '202001.csv']

# first file:
with open("merger.csv","w") as fout:

    with open("output/201512.csv") as f1:
        for line in f1.readlines():
            fout.write(str(line))
        f1.close()

    # now the rest:
    for file in files:
        with open("output/"+file) as f:
            for idx,line in enumerate(f.readlines()):
                if idx != 0:
                    fout.write(str(line))
            f.close()  # not really needed
    fout.close()
