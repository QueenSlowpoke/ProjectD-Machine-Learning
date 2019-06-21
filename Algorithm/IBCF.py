import pandas as pd
import numpy as np
import sklearn as sk
import sys


# ***Experiment with ItemBasedCollabrativeFiltering***

emItem = pd.read_csv('./Count.csv', sep=";")

# convert data to interger
emItem["EmployeeId"] = emItem["EmployeeId"] .astype(np.int64)
emItem["InventoryId"] = emItem["InventoryId"] .astype(np.int64)
emItem["CountItem"] = emItem["CountItem"] .astype(np.int64)

# put the data in a matrix between userId and product ID with the amountborrowed(CountItem) as value
dfMatrix = pd.pivot_table(emItem, values='CountItem', index='EmployeeId', columns='InventoryId')
# print(dfMatrix) #uncomment to see the matrix in console

#normalise the data between userId and productID
dfMatrixNorm = (dfMatrix-dfMatrix.min())/(dfMatrix.max()- dfMatrix.min())

#look up the correlation between the products
dfMatrixCorr = dfMatrixNorm.corr()

#find the items that userId 14190 has borrowed 
myRatings = dfMatrix.loc[4].dropna()

#create a one dimensional array to hold recommendation items
similarityCandidates = pd.Series()

#logic of the recommender 
for i in range(0, len(myRatings.index)):
    print ("Adding similarities for " + str(myRatings.index[i]) + "...")
    #retrieve similar items where are correlation between them
    similarity = dfMatrixCorr[myRatings.index[i]].dropna()
    
    #scale its sililarity based on correlation value
    similarityMap = similarity.map(lambda x: x * myRatings.index[i])


    #add the score to the list of similarity candidates 
    similarityCandidates = similarityCandidates.append(similarityMap)
    #getting rid of negative numbers
    similarityCandidates = similarityCandidates.where(similarityCandidates > 0)

#first raw result
similarityCandidates.sort_values(inplace = True, ascending = False)
# print(similarityCandidates) #uncomment to see raw result

# clean up the output by getting rid of duplicates
similarityCandidates = similarityCandidates.groupby(similarityCandidates.index).sum()

# sort the cleaned up result and return the top 10 recommended items
print("Sorting result...") 
similarityCandidates.sort_values(inplace = True, ascending = False)
print(similarityCandidates.head(10))


# ***EXTRA*** filter out the items that the users already have borrowed once
# why? maybe those items are terminated therefore you want to filter those out but still want to give out items that are correlated with that item.
# filterSimilarities = similarityCandidates.drop(myRatings)
# print(filterSimilarities)