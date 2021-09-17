
from pyexcel_xls import get_data

# excel_sheet = get_data('test.xls')
# print(excel_sheet['Sheet1'][0])
def saveToDb(file):
    excel_sheet = get_data(file)	
    for lst in excel_sheet['Sheet1']:
        question = lst[0]
        op1 = lst[1]
        op2 = lst[2]	
        op3 = lst[3]		
        op4 = lst[4]		
        cans = lst[5]			
        vals = (question,op1,op2,op3,op4,cans)
        print(vals)
saveToDb("test.xls")