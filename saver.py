from pathlib import Path
import pymongo

# #conect to server
# client = pymongo.MongoClient('mongodb://localhost:27017')
# # create database
# db = client['db']
# # create collection ( = table in SQL)
# collection  = db['collection']

# droped = collection.drop()
# # prepare document (=  record in SQL)

# # insert document
# #fetch:
# # find one: return  documents
# # find: return an iterable of documents
# # find ({} [query obj]->  SELECT (where query obj, if empty ->*), {...} -> which fields ('cols') to show)
# collection.update({'Mike':{'$exists':True}}, {'$push':{'Mike':1}}, upsert=True)

# f = collection.find({})
# for c in f:
#     try:
#         print(c['Mike'])
#     except:
#         print( f)
# collection.update({'Mike':{'$exists':True}}, {'$push':{'Mike':2}}, upsert=True)

# f = collection.find({})
# for c in f:
#     try:
#         print(c['Mike'])
#     except:
#         print( f)
# delete document


class Saver:

    '''
        MongoDB database. Stores tags in the form of : {Tag:[img1_path, img2_path...]}
    '''
    def  __init__(self, db_scheme):
        self.client = pymongo.MongoClient(db_scheme)
        self.db = self.client['Tags']
        self.collection = self.db['TagsCollection']


    def save(self, path,*tags ):
        '''Upsert collection for every tag tagged by user: if tag already exist: push new img to dociment, else: cretae{tag:[img_path]}'''
        print(tags)
        for t in tags:
            self.collection.update({t:{'$exists':True}}, {'$push':{t:path}}, upsert=True)

    def get_tag_path(self, tag):
        try:
            res  = self.collection.find_one({tag:{'$exists':True}})
            return res[tag]
        except TypeError:
            return []
       

    def drop_collection(self):
        self.collection.drop()



def test ():
    saver = Saver('mongodb://localhost:27017')
    saver.drop_collection()
    img_lst = [f for f in Path.cwd().iterdir() if '.png' in str(f)]
    for i in range(len(img_lst)):
        saver.save(str(img_lst[i]), 'test'+str(i))
    for i in range(len(img_lst)):
        tag = 'test'+str(i)
        res = saver.get_tag_path(tag)
        print(tag, res)


if __name__ == '__main__':
    print('Start testing')
    test()
