declare -a arr=('201512.pdf' '201601.pdf' '201602.pdf' '201603.pdf' '201604.pdf' '201605.pdf' '201606.pdf' '201607.pdf' '201608.pdf' '201609.pdf' '201610.pdf' '201611.pdf' '201612.pdf' '201701.pdf' '201702.pdf' '201703.pdf' '201704.pdf' '201705.pdf' '201706.pdf' '201707.pdf' '201708.pdf' '201709.pdf' '201710.pdf' '201711.pdf' '201712.pdf' '201801.pdf' '201802.pdf' '201803.pdf' '201804.pdf' '201805.pdf' '201806.pdf' '201807.pdf' '201808.pdf' '201809.pdf' '201810.pdf' '201811.pdf' '201812.pdf' '201901.pdf' '201902.pdf' '201903.pdf' '201904.pdf' '201905.pdf' '201906.pdf' '201907.pdf' '201908.pdf' '201909.pdf' '201910.pdf' '201911.pdf' '201912.pdf' '202001.pdf' )    ## now loop through the above array
for i in "${arr[@]}"
do
    echo "Generating $i" 
    python read_pdf.py "data/$i"     
done