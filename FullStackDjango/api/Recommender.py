"""
First all the needed methods are imported:
Pandas is a data structure and analysis tool supporting data analysis workflow. 
Numpy supports the mathematical calculations that must be done. 
Mathplotlib has the ability to portray the data in graphs. 
SciPy is a package that optimalizes linear algebra and statistics. 
Itertools is used for efficient looping through data.
Random is used to generate random numbers.
"""
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from django.db import connection
import itertools
import random

"""
The class Recommender is created. A class is a set of objects having
some attributes in common. It is a blueprint for individual objects
with exact behaviour. __init__ is known as a constructor. This method
is called  when an object is created from the class and it allows the
class to initialize the attributes of a class. In the def __init__
UserId is made global and data received from the database is converted
to be able to use it for the algoritm and to make it compatible with
the rest of the website.
"""

class Recommender:
    def __init__(self, UserId):
        self.UserId = UserId   
        self.inventory = self.PandaFormatting("SELECT * FROM api_product", ["ProductId", "title", "brand", "image", "price", "category"]) 
        self.employeeList = self.PandaFormatting("SELECT * FROM api_user", ["UserId", "password", "last_login","email","active","staff","admin","firstname", "lastname","timestamp", "jobtitle"])
        self.countItems = self.PandaFormatting("SELECT u.id, pl.product_id, SUM(pl.amount) FROM api_user AS u JOIN api_order AS o ON u.id = o.user_id JOIN api_productlist AS pl ON o.id = pl.order_id GROUP BY u.id, pl.product_id", ["UserId", "ProductId", "Count"])
        self.employeeWitem = self.PandaFormatting("SELECT o.id, o.user_id, pl.product_id, pl.amount FROM api_order AS o JOIN api_productlist AS pl ON o.id = pl.order_id ORDER BY o.id, o.user_id, pl.product_id;", ["OrderId", "UserId", "ProductId", "amount"])
        #self.DataFiltering()

    def PandaFormatting(self, query, columnName):
        fetchData = connection.cursor().execute(query)
        dataframe = pd.DataFrame(list(fetchData.fetchall()))
        dataframe.columns = columnName
        dataframe.index += 1
        return dataframe 
        
    """
    A value called newCount is made. It consists of the global variable
    countItems. countItems is the converted data from the database which
    shows the userID and the productID of the borrowed product + the 
    total amount of the referring product that has been borrowed. The new
    self.countItems filters out products which have been borrowed <2.
    """
    def DataFiltering(self):
        newCount = self.countItems["UserId"].value_counts()
        self.countItems = self.countItems[self.countItems["UserId"].isin(newCount[newCount < newCount[1]].index)]
      
    """
    GetTopBorrowedItems is a simple groupby function to get the top borrowed
    items from the database. totalCountPerItem adds the amount of times an 
    item has been borrowed. toprecommendedItems merges the results of the
    totalCountPerItem with the inventory
    """
    def GetTopBorrowedItems(self, num):
        totalCountPerItem = pd.DataFrame(self.countItems.groupby(['ProductId'])['Count'].sum())
        print(totalCountPerItem) 
        toprecommendedItems = pd.merge(totalCountPerItem.sort_values("Count", ascending=False), self.inventory, on="ProductId")
        recommendList = toprecommendedItems.head(num)

        dropColumns = ["Count", "brand", "image", "price", "category"] 
        recommendList = recommendList.drop(dropColumns, axis=1) 
        recommendList = recommendList.sample(frac=1).reset_index(drop=True)
        resList = []
        for i in range(len(recommendList)):
            resList.append([recommendList["ProductId"][i], recommendList["title"][i] ])
        print(resList)
        return resList

    """
    CheckAndGetHistory will first call the CreateUserHistoryArray to get an
    array based on the user's history. If the history appears to be empty
    (with other words, when a new user wants to make use of the system),
    a related recommandation based on the new user's function within the 
    company will show. This is done based on the history of a random
    user with the same function. After the for-loop the fuction
    CreateUserHistory is called, but this time with a random employee ID. In
    the end, the function returns an array with productID's (NOT oderID's).
    """
    def CheckAndGetHistory(self):
        hist = self.CreateUserHistoryArray(self.UserId)
        haveHist = True

        if len(hist) == 0:
            haveHist = False
            userIdArray = []
            jobTitle = self.employeeList.loc[(self.UserId), "jobtitle"]
            print(jobTitle)          
            sameFunction = self.employeeList['UserId'].where(self.employeeList['jobtitle'] == jobTitle).dropna()
            for i in sameFunction:
                if int(i) <= 30:
                    userIdArray.append(int(i))
            randomId = random.choice(userIdArray)
            hist = self.CreateUserHistoryArray(randomId)
        return hist, haveHist

    """
    In the CreateUserHistoryArray functon, two empty lists are made. One for
    the history of the OrderId and one of the products, filled with the 
    ItemId's. The first for-loop loops through all the previously made
    orders and adds the order to the hist list if the UserId of the user
    that has made the order, matches the UserId of the current user. After
    all the orders are added, the order of the list is reversed so that the
    most 'recent' order is on top of the list. The second for-loop adds all
    the ProductId's of all the matching orders to the product list. After that
    all the duplicates are dropped. After that only the five most recent items
    are shown.
    """
    def CreateUserHistoryArray(self, Id):
        hist = []
        product = []
        for row in range (1, (len(self.employeeWitem))):
            if self.employeeWitem["UserId"][row] == Id:
                hist.append(self.employeeWitem["OrderId"][row])
        hist.sort(reverse = True)
        for i in hist:
            product.append(self.employeeWitem.at[(i), "ProductId"])
        product = list(dict.fromkeys(product)) 
        if len(product) > 5:
            del product[5::] 
        return product

    """
    The algorithm starts with combining columns that are needed for the
    algorithm and dropping the ones that are not needed. For instance the
    count data, together with the data of the total amount count, they are
    combined. Based on the adjusted data, a matrix is formed. After importing 
    NearestNeigbours from sklearn.neighbors, a knn model is created. This is 
    filled with the matrix. queryIndex will go to the global function
    CheckAndGetHistory to get an array filled with relevant items. 
    
    The first for-loop loops through the array to get the distances. Within
    the loop is a try except just in case new products would be added to the
    database and there is only one neighbor. Each of the distances are then 
    added to the previously empty list ItemId. Afterwards, a new empty list
    called idList is made fot the second for-loop. The second for loop loops
    through the items in the ItemId list and adds one to the index due to the
    index starting at 0 and the products starting at 1. The value of the array
    is obviously used to find the ID of the products in the database.

    IMPORTANT NOTES - Take a look at this later:
    In pandas the index starts at 0. Unlike SQL, where the index starts at 1. 
    Since we need to look up items in the inventory, employewithitem and
    employeelist, it will make the job easier by setting the index at 1, 
    so we don't have to add 1 the whole time while writing code.

    Due to the top 1 percent being a small amount borrowed items, we took the top 5-6% instead.
    quantile = productAmountCount['totalAmountCount'].quantile(np.arange(.9, 1, .01)).mean()
    print(quantile)
    """
    def Knn(self, productHistoryList):
        combineItemCount = pd.merge(self.countItems, self.inventory, on="ProductId")
        print('---------------------------------------------------------------------')
        dropColumns = ["brand", "image", "price", "category"] 
        combineItemCount = combineItemCount.drop(dropColumns, axis=1) 
        combineItemCount = combineItemCount.dropna(axis = 0, subset = ['title'])
        productAmountCount = (combineItemCount.groupby(by= ['title'])['Count'].sum().reset_index().rename(columns = {'Count': 'totalAmountCount'})[['title', 'totalAmountCount']])
        countWithTotal = combineItemCount.merge(productAmountCount, left_on = "title", right_on = 'title', how= 'left')

        CountpopluarItem = countWithTotal
        CountpopluarItem = CountpopluarItem.drop_duplicates(['UserId', 'title'])
        CountpopluarItemPivot = CountpopluarItem.pivot(index = "ProductId", columns = 'UserId', values = 'Count').fillna(0)
        CountpopluarItemMaxtrix = csr_matrix(CountpopluarItemPivot.values)

        from sklearn.neighbors import NearestNeighbors

        model_knn = NearestNeighbors(metric= 'cosine', algorithm= 'brute')
        model_knn.fit(CountpopluarItemMaxtrix)
        ItemId = []

        for index in productHistoryList:
            try:
                distances, indices = model_knn.kneighbors(CountpopluarItemPivot.loc[int(index), :].values.reshape(1, -1), n_neighbors=4)
            except:
                distances, indices = model_knn.kneighbors(CountpopluarItemPivot.loc[int(index), :].values.reshape(1, -1), n_neighbors=2) #new products might ot have many short disntace porducts close to them
            
            for i in range(1, len(distances.flatten())):
                duplicate = indices.flatten()[i]+1 in (item for sublist in ItemId for item in sublist)
                print(duplicate)
                if duplicate == False:
                    ItemId.append([(indices.flatten()[i]+1), distances.flatten()[i]])
        
        if len(ItemId) > 10:
            del ItemId[10::] 
        
        ItemId = sorted(ItemId, key= lambda x: x[1]) 
        #print(ItemId)
        idList = []

        recommendedProducts = []
        index = 0
        while index < len(ItemId):
            recommendedProducts.append([ItemId[index][0],self.inventory.at[ItemId[index][0], "title"], ItemId[index][1]])
            index = index + 1
        #print(recommendedProducts)
        return recommendedProducts
