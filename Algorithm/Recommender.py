"""
First all the needed methods are imported:
Pandas is a data structure and analysis tool supporting data analysis workflow. 
Numpy supports the mathematical calculations that must be done. 
Mathplotlib has the ability to portray the data in graphs. 
SciPy is a package that optimalizes linear algebra and statistics. 
Itertools is used for efficient looping through data.
Random is used to generate random numbers.
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.sparse import csr_matrix
import itertools
import random

class Recommender:
    def __init__(self, inventory, countItems, employeeWitem, UserId, employeeList):
        """
        The class Recommender is created. A class is a set of objects having
        some attributes in common. It is a blueprint for individual objects
        with exact behaviour. __init__ is known as a constructor. This method
        is called  when an object is created from the class and it allows the
        class to initialize the attributes of a class. After initializing, 
        arguments are given before diving into the 'main' part of the
        constructor. In the body, the arguments that were given are also the 
        attributes that the program is going to work with. 'self.' represents
        the instance of the class. By using the self keyword, we can make a
        class, object or attribute global instead of just local.
        The following attributes are made global. After this the  program goes
        to the function datafiltering, which has also been made global.
        """
        # in panda the ondex start with 0. unlike SQL that start with 1 
        # since we need to look up in inventory, employewithitem & employeelist
        # it will make thej ob easier by setting the index at 1 so we don't have to.
        # add 1 the whole time while writing code
        self.inventory = inventory
        self.countItems = countItems
        self.employeeWitem = employeeWitem
        self.employeeWitem.index += 1 
        self.UserId = UserId
        self.employeeList = employeeList
        self.employeeList.index += 1 
        self.DataFiltering()

    #simpel groupby function to get top borrowed Items
    def GetTopBorrowedItems(self, num):
        #count x amount time that a item have been borrowed
        totalCountPerItem = pd.DataFrame(self.countItems.groupby(['ProductId'])['Count'].count())

        #merge total count Per Item with inventory 
        toprecommendedItems = pd.merge(totalCountPerItem.sort_values("Count", ascending=False), self.inventory, on="ProductId")

        return toprecommendedItems.head(num)

    def DataFiltering(self):
        """
        A value called newCount is made. It consists of the global variable
        countItems. countItems is the data of the Count.csv file TBC
        """
        newCount = self.countItems["Count"].value_counts()
        # filter out products with borrow rate < 2
        self.countItems = self.countItems[self.countItems["Count"].isin(newCount[newCount < newCount[1]].index)]

    def CheckAndGetHistory(self):
        #so at the start it will call CreateUserHistoryArry to get an array
        #based on their history
        hist = self.CreateUserHistoryArray(self.UserId)
        print("history of current user:")

        if len(hist) == 0:
            # new employee won't have a order history
            # to give them a related recommendation based on their function
            # we get a history from a random employee with the some function
            userIdArray = []
            jobTitle = self.employeeList.loc[(self.UserId), "jobtitle"]
            print(jobTitle)          
            sameFunction = self.employeeList['UserId'].where(self.employeeList['jobtitle'] == jobTitle).dropna()
            for i in sameFunction:
                if int(i) <= 30:
                    userIdArray.append(int(i))
            randomId = random.choice(userIdArray)
            print("history from random user")
            #call the function CreateUserHistoryArry but this time with a random employee ID
            hist = self.CreateUserHistoryArray(randomId)

        print("previous borrowed items:")
        print(hist)

        #in the end it return an array with product id NOT order id
        return hist

    def CreateUserHistoryArray(self, Id):
        hist = [] #history of Order ID
        product = [] #fill with Items ID

        #this for loop needs to be re-written when database is involed 
        #because there are chances that an oder contains multiple products
        for row in range (1, (len(self.employeeWitem))):
            if self.employeeWitem["UserId"][row] == Id:
                hist.append(self.employeeWitem["OrderId"][row])
                #print("Item added")
        hist.sort(reverse = True)

        # add item id based on orderId to the product array
        for i in hist:
            product.append(self.employeeWitem.at[(i), "ProductId"])
        
        #drop duplicates item id
        product = list(dict.fromkeys(product)) 
        
        # only save the 5 most recent ID 
        if len(product) > 5:
            del product[5::] 

        return product
        

    def Knn(self):
        # combine and drop the columns that is not needed for the algoritm
        combineItemCount = pd.merge(self.countItems, self.inventory, on="ProductId")
        dropColumns = ["Brand", "Image", "Price", "Category"] 
        combineItemCount = combineItemCount.drop(dropColumns, axis=1) 

        #drop NA
        combineItemCount = combineItemCount.dropna(axis = 0, subset = ['Title'])

        productAmountCount = (combineItemCount.groupby(by= ['Title'])['Count'].sum().reset_index().rename(columns = {'Count': 'totalAmountCount'})[['Title', 'totalAmountCount']])
   
        
        #combine count data with total amount count data 
        countWithTotal = combineItemCount.merge(productAmountCount, left_on = "Title", right_on = 'Title', how= 'left')
        # print(countWithTotal)
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                #Take a look at this later
        #due to top 1 percent is a small amount of borrowed item we took the top 5-6% instead.
        # quantile = productAmountCount['totalAmountCount'].quantile(np.arange(.9, 1, .01)).mean()
        # print(quantile)
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

        CountpopluarItem = countWithTotal

        CountpopluarItem = CountpopluarItem.drop_duplicates(['UserId', 'Title'])
        CountpopluarItemPivot = CountpopluarItem.pivot(index = "ProductId", columns = 'UserId', values = 'Count').fillna(0)
        CountpopluarItemMaxtrix = csr_matrix(CountpopluarItemPivot.values)

        from sklearn.neighbors import NearestNeighbors

        model_knn = NearestNeighbors(metric= 'cosine', algorithm= 'brute')
        model_knn.fit(CountpopluarItemMaxtrix)

        queryIndex = self.CheckAndGetHistory()
        ItemId = []
        for index in queryIndex:
            try:
                distances, indices = model_knn.kneighbors(CountpopluarItemPivot.loc[int(index), :].values.reshape(1, -1), n_neighbors=3)
            except:
                # in case for new products and there is only 1 neighbour
                distances, indices = model_knn.kneighbors(CountpopluarItemPivot.loc[int(index), :].values.reshape(1, -1), n_neighbors=2)
            
            for i in range(1, len(distances.flatten())):
                ItemId.append([indices.flatten()[i], distances.flatten()[i]])
        
        ItemId = sorted(ItemId, key= lambda x: x[1])
        
        print(ItemId)
        idList = []
        # plus one because of index start at 0 and product start at 1.
        #value from the array is to use to find the ID in DB 
        for item in ItemId:
            idList.append((item[0] + 1))

        idList = list(dict.fromkeys(idList))  
        print("for web application no duplicate ID:")
        print(idList)
        # Needed this return for web application to give an array of product Id and find them in the DB
        # return idList


        #extra for testing in console so it returns a array with name and distance. 
        #for testing the index does not have to increase with one because the tabel with products in datafram starts with 0 instead of 1
        print("---------------------------------------------")
        print("test log for console with duplicates and distance")
        recommendedTitles = []
        index = 0
        while index < len(ItemId):
            recommendedTitles.append([self.inventory.at[ItemId[index][0], "Title"], ItemId[index][1]])
            index = index + 1

        return recommendedTitles