import pymongo
from pymongo import MongoClient

client = pymongo.MongoClient('localhost',27017)
myDb = client["myDb"]
myCol = myDb["myCol"]
mydict = { "name": "John", "address": "Highway 37" }

x = myCol.insert_one(mydict)
print(x.inserted_id)

print myDb.close()
print client.close()