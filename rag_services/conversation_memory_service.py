import  os, json

from langchain_core.messages import HumanMessage, AIMessage

class ConversationMemoryStorage:
    
    def __init__(self):
        self.storage = "chat_history.json"
        if not os.path.exists(self.storage):
            with open(self.storage, "w") as file:
                json.dump(None, file, indent=4)

    def store_conversation_memory_data(self, thread_id, chat_history):
        data = [{'human': chat_history[-2].content,
                 'ai': chat_history[-1].content,
                 'thread_id': 'yash111', }]
        with open(self.storage, "r+") as file:
            try:
                file_content = file.read().strip()
                existing_data = json.loads(file_content) if file_content else []
            except json.JSONDecodeError:
                existing_data = []
            existing_data.extend(data)
            file.seek(0)
            json.dump(existing_data, file, indent=4)
        return "Successfully stored conversation."

    def pass_conversation_memory(self, memory, thread_id):
        with open(self.storage, "r") as file:
            file_content = file.read().strip()
            if not file_content:
                print("no data there")
                return  "no data"
            file_data = json.loads(file_content)
            filtered_data = [item for item in file_data if item.get("thread_id") == thread_id]
            for data in filtered_data:
                stored_conversation = [
                    HumanMessage(content=data.get('human')),
                    AIMessage(content=data.get('ai'))
                ]
                memory.chat_memory.messages.extend(stored_conversation)
        return "successfully added previous data into memory"
                
           
        
    
        
    