import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.sparse import csr_matrix
countItems = pd.read_csv('./Count.csv', sep=";")
inventory = pd.read_csv('./DataSets/LaptopsV2.csv')

# convert data to interger
inventory["ProductId"] = inventory["ProductId"].astype(np.int64)

countItems["UserId"] = countItems["UserId"].astype(np.int64)
countItems["ProductId"] = countItems["ProductId"].astype(np.int64)
countItems["Count"] = countItems["Count"].astype(np.int64)

# control if everything is correct
# print(countItems.head())
# print(inventory.head())

#check how the count is distributed, example how often is a product borrowed for 10 times  
plt.rc("font", size=11)
countItems.Count.value_counts(sort=False).plot(kind='bar')
plt.title('Count distribution')
plt.xlabel("num of Count")
plt.ylabel("count of total")
# plt.show()

#count how x amount time that a item have been borrowed.
totalCountPerItem = pd.DataFrame(countItems.groupby(['ProductId'])['Count'].count())
totalCountPerItem.sort_values("Count", ascending=False)
# print(totalCountPerItem.sort_values("Count", ascending=False).head())

#get the top items that have been borrowed the most (not machine learning but might be usefull for web application)
toprecommendedItems = pd.merge(totalCountPerItem.sort_values("Count", ascending=False), inventory, on="ProductId")
# print(toprecommendedItems.head())
# print("-------------------------------------------------------------")

#recommendation based on correlation 
avarageCount = pd.DataFrame(countItems.groupby(['ProductId'])['Count'].mean())
avarageCount['meanCount'] = pd.DataFrame(countItems.groupby(['ProductId'])['Count'].count())
print(avarageCount.sort_values("Count", ascending=False).head())
print("-------------------------------------------------------------")

#exclude count with less than 2
newCount = countItems["Count"].value_counts()
# print(newCount)
countItems = countItems[countItems["Count"].isin(newCount[newCount < newCount[1]].index)]
# print(countItems)

#make a matrix
countPivot = countItems.pivot(index='UserId', columns='ProductId').Count
UserID = countPivot.index
ProductId = countPivot.columns
# print(countPivot.head())

# find correlation with productID
myRatings = countPivot[10]
similarity = countPivot.corrwith(myRatings)
corrSimilarity = pd.DataFrame(similarity, columns=['pearsonR'])
corrSimilarity.dropna()
corrSummary = corrSimilarity.join(avarageCount['meanCount'])
sortedSummary = corrSummary[corrSummary['meanCount'] >= 2].sort_values('pearsonR', ascending=False).head(10)
# print(sortedSummary)

topTen = sortedSummary.index
# print(topTen)

itemsCorrToMyRatings = pd.DataFrame(topTen, index= np.arange(10), columns=['ProductId'])
corrItems = pd.merge(itemsCorrToMyRatings, inventory, on='ProductId')
print(corrItems)


#-------------------------------------------------------------------------------------------------------
#knn setup
combineItemCount = pd.merge(countItems, inventory, on="ProductId")
dropColumns = ["Brand", "Image", "Price"] 
combineItemCount = combineItemCount.drop(dropColumns, axis=1) 
# print(combineItemCount.head())


combineItemCount = combineItemCount.dropna(axis = 0, subset = ['Title'])

productAmountCount = (
    combineItemCount.groupby(by= ['Title'])['Count'].count().reset_index().rename(columns = {'Count': 'totalAmountCount'})[['Title', 'totalAmountCount']]
)

#combine count data with tot amount count data 
countWithTotal = combineItemCount.merge(productAmountCount, left_on = "Title", right_on = 'Title', how= 'left')
# print(countWithTotal)

#statistics of total count 
pd.set_option('display.float_format', lambda x: '%.3f' % x)
# print(productAmountCount['totalAmountCount'].describe())

print(productAmountCount['totalAmountCount'].quantile(np.arange(.9, 1, .01)))
# top 1 percent is around 19times borrowed, however there aren't many items in the top 1% therefore we take the top 10% items with is around 12
print("--------------------------------------------------------------------")
quantile = productAmountCount['totalAmountCount'].quantile(np.arange(.9, 1, .01))



popularity = int(quantile.mode())
print(popularity)
CountpopluarItem = countWithTotal.query('totalAmountCount >= @popularity')
# print(CountpopluarItem)

#------------------------------------------------------------------------------------------------
#knn inplementation

CountpopluarItem = CountpopluarItem.drop_duplicates(['UserId', 'Title'])
CountpopluarItemPivot = CountpopluarItem.pivot(index = "Title", columns = 'UserId', values = 'Count').fillna(0)
CountpopluarItemMaxtrix = csr_matrix(CountpopluarItemPivot.values)

from sklearn.neighbors import NearestNeighbors

model_knn = NearestNeighbors(metric= 'cosine', algorithm= 'brute')
model_knn.fit(CountpopluarItemMaxtrix)

queryIndex = np.random.choice(CountpopluarItemPivot.shape[0])
distances, indices = model_knn.kneighbors(CountpopluarItemPivot.iloc[queryIndex, :].values.reshape(1, -1), n_neighbors=6)



for i in range(0, len(distances.flatten())):
    if i == 0:
        print('Recommendations for {0}:\n'.format(CountpopluarItemPivot.index[queryIndex]))
    else:
        print('{0}: {1}, with distance of {2}:'.format(i, CountpopluarItemPivot.index[indices.flatten()[i]], distances.flatten()[i]))


# De functie moet een array van user history accepteren 
# voor ieder loop voeg die de top 3 in de lijst
# how to find accuracy
# dan order die de lijst 
# geeft terug  