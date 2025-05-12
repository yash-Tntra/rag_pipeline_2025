from langchain.schema import BaseMessage
from langchain.schema.messages import messages_to_dict, messages_from_dict
from langchain_core.chat_history import BaseChatMessageHistory
from pymongo import MongoClient


class ConversationMemoryStorage(BaseChatMessageHistory):
    def __init__(self, session_id: str, memory):
        self.session_id = session_id
        self.connection = "mongodb://localhost:27017/"
        self.client = MongoClient(self.connection)
        self.collection = self.client['memory_db']['conversations']
        self.messages = []
        
        existing = self.collection.find_one({"session_id": self.session_id})
        if existing:
            self.messages = messages_from_dict(existing["messages"])
            memory.chat_memory.messages = self.messages
        
        else:
            self.collection.insert_one({
                "session_id": self.session_id,
                "messages": messages_to_dict(self.messages)
            })
    
    def add_message(self, message: BaseMessage) -> None:
        self.messages.append(message)
        self.collection.update_one(
            {"session_id": self.session_id},
            {"$set": {"messages": messages_to_dict(self.messages)}}
        ),
        print(f"Message added to session: {self.session_id}")
        
       
    
    def clear(self) -> None:
        self.messages = []
        self.collection.update_one(
            {"session_id": self.session_id},
            {"$set": {"messages": []}}
        )
        print(f"Message added to session: {self.session_id}")
 
                
           
        
    
        
    