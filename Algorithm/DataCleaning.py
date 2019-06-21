import pandas as pd
import numpy as np
import sklearn as sk
import sys

# inv_col = ['InventoryId']
# inventory = pd.read_csv("./DataSets/inventory.csv", sep=";", names=inv_col, usecols=[0])
employeeWitem = pd.read_csv	("./DataSets/OrderHistoryV5.csv", sep=";", usecols=[1,2])

employeeWitem = employeeWitem.groupby(['UserId', 'ProductId']).size().to_frame('Count')
# df.columns = ["UserID", "ProductID", "Count"]
# employeeWitem["Mean"] = employeeWitem.apply(employeeWitem["Count"].mean(), axis = 1)
# print(employeeWitem)
employeeWitem.to_csv("CountV5-2.csv", sep=';', encoding="utf-8")

