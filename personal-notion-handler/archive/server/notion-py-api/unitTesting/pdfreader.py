# importing required modules 
from pdfminer.high_level import extract_text
from tabula import read_pdf

testFile = "/mnt/c/Users/cjuns/Downloads/testing.pdf"
df = read_pdf(testFile,multiple_tables=True,pages='2')
print(df)
# text = extract_text(testFile)
 
# print(text)