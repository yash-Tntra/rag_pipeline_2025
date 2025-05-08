from pymongo import MongoClient

class MongoDBService:
    def __init__(self):
        self.client = MongoClient("mongodb://localhost:27017/")
        
        self.db = self.client['memory_db']
        self.collection = self.db['conversations']
        
    def store_data(self, messages):
        self.collection.insert_one(messages)
        return "Message stored successfully!"
        
    def get_data(self, thread_id):
        messages = self.collection.find({"thread_id": thread_id})
        return messages

    
    

        
        
