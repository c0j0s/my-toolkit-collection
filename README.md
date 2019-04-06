# PythonPPT
This project contains scripts that generate PPT slides base on txt inputs, so to avoid manual work creating slides for the hundered over lines of captions.  

The txt inputs here were reduce for confidentiality purpose.

Input Files:  
```
raw.txt  
combileLine.txt  
split.csv  
base.ppt
```
Python Scripts:  
```
prepareDualLine.py  
prepareCSV.py  
preparePPT.py  
```
Output Files:   
```
output.pptx  
```

## Procedures
__1. Prepare Raw TXT Inputs__  
As the scenario here is to create slices with Chinese and English captions, the raw txt input is been formatted to remove any unnecessary characters and create a fix Chinese after English caption format for easy processing.  

__2. Format TXT Inpits__  
Next the captions were merged to create a csv with both languges side by side such that each line represents a slide in txt form.

__3. Generate PPT Slides__  
Next, a base ppt containting the desired slide design is been created using Microsoft PowerPoint. Finally execute the preparePPT script which takes in the txt inputs and created all the slides automatically.