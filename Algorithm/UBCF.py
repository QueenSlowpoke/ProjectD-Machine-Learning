import pandas as pd
import numpy as np
import sklearn as sk
import sys
import csv
import random

emItem = pd.read_csv('./CountTest.csv', sep=";")

# convert data to interger
emItem["UserId"] = emItem["UserId"] .astype(np.int64)
emItem["ProductId"] = emItem["ProductId"] .astype(np.int64)
emItem["Count"] = emItem["Count"] .astype(np.int64)

msk = np.random.rand(len(emItem)) < 0.8

trainingSet = emItem[msk]
testSet = emItem[~msk]

print("train:" + repr(len(trainingSet)))
print("test:" + repr(len(testSet)))

# print(testSet)

productAgg = trainingSet.groupby("ProductId").agg({"Count": {np.size, np.mean}})
# print(productAgg)
# ProductIdRating = pd.DataFrame(productAgg['CountItem']['size'])
# NormalizedProductIdRating = ProductIdRating.apply(lambda x: (x - np.min(x))/ (np.max(x) - np.min(x)))
# print(NormalizedProductIdRating)

# v is borrow item count - check

# m is minimum count required to be listed 
M = productAgg["Count"]["size"].quantile(0.9)
print(M)
# r is avarage count of product - check
# C is the mean count across the whole dataframe aka how often has a item been borrowed 
C = productAgg['Count']['mean'].mean()
print(C)

qualified = productAgg.copy().loc[productAgg["Count"]["size"] >= M]

print(len(qualified)) 
print(qualified) 

#function to compute the weighthe count borrowed of each product
def weigthedCountItem(M, C):
    V = productAgg["Count"]["size"]
    R = productAgg["Count"]["mean"]
    return(V/(V+M) * R) + (M/(M+V) * C)


Score = weigthedCountItem(M,C)
qualified.insert(2, "Score", Score)
print(qualified)


