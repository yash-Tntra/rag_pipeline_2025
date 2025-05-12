import asyncio
import logging
import os
import uuid
import json
from langchain.chains.conversation.base import ConversationChain
from langchain.chains import ConversationalRetrievalChain
from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain_community.chat_message_histories import MongoDBChatMessageHistory
from langchain_community.llms.ollama import Ollama
from langchain_core.callbacks import StreamingStdOutCallbackHandler
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import HumanMessagePromptTemplate
from datetime import datetime

from rag_services.conversation_memory_service import ConversationMemoryStorage
from rag_services.enahnce_and_clean_data_service import EnhanceService
from rag_services.web_search_service import WebScrapService
from langchain.memory import ConversationBufferMemory, CombinedMemory
from rag_services.embedding_vector_store_service import EmbeddingVectorStore
from langchain.retrievers import EnsembleRetriever, ContextualCompressionRetriever
from langchain.prompts import ChatPromptTemplate
from constant.prompt_constant import ROUTE_SELECTOR




class RagPipeline:

    def __init__(self):
        self.current_datetime = datetime.now()
        self.llm = Ollama(model= "llama3", callbacks=[StreamingStdOutCallbackHandler()], temperature=0.2)
        self.memory =  ConversationBufferMemory(memory_key="history", return_messages=True)
        self.chat_history = self.memory.load_memory_variables({})['history']
        self.qa = ConversationChain(llm=self.llm, memory=self.memory, verbose=True)
    

    def check_where_to_go(self, prompt):
       
        query_classification = ROUTE_SELECTOR.format(prompt)
        system_selector = self.llm.invoke(query_classification)
        logging.debug(f"selector is {system_selector}")
        return system_selector

    def execute_query(self, prompt, thread_id):
        # llm_query = EnhanceService(self.llm).prompt_enhance_service(prompt)
       
        keyword = self.check_where_to_go(prompt)
        keyword_executor = {
            "Rag": self.rag_call,
            "LLM": self.llm_call
        }
        return keyword_executor.get(keyword, self.rag_call)(prompt, thread_id)

    def rag_call(self, query, thread_id):
        # web scrap module and documents
        # prompt = f" FYI Please consider the current time and date: {self.current_datetime}"
        # rag_query = query + prompt
        documents = asyncio.run(WebScrapService().duckduckgo_search_and_scrape(query.content))
        vectorstore, bm25_retriever = EmbeddingVectorStore().embedding_vector_store_service(documents)
        retriever = vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={
                "k": 2,
            }
        )
        
        # todo : here we will pass thred id which neeed to fetch

        hybrid_retriever = EnsembleRetriever(
                retrievers=[retriever, bm25_retriever],
                weights=[0.5, 0.5]
            )

        # reranker = LLMReranker(llm=self.llm)
        #
        # compression_retriever = ContextualCompressionRetriever(
        #     base_compressor=reranker,
        #     base_retriever=hybrid_retriever
        # )
        #
        rag_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=hybrid_retriever,
            memory=self.memory,
            verbose=True
        )
        result = rag_chain.run(query.content)
        result = AIMessage(content=result)
        # enhance_response = EnhanceService(self.llm).review_llm_result(query, result)
        ConversationMemoryStorage(thread_id, self.memory).add_message(result)
        

    def llm_call(self, query, thread_id):
        breakpoint()
        result = self.qa.run(query.content)
        result = AIMessage(content=result)
        ConversationMemoryStorage(thread_id, self.memory).add_message(result)

        # enhance_response = EnhanceService(self.llm).review_llm_result(query, result)
        # ConversationMemoryStorage().store_conversation_memory_data(thread_id, self.chat_history)
        return  result
    
    def handle_conversation(self):
        print("Ask me:)--------------------")
        query = input()
        # thread_id = str(uuid.uuid4())
        thread_id = 'be0cbca2-7520-482f-bb00-66f22e7465b3'
        query = HumanMessage(content=query)
        ConversationMemoryStorage(thread_id, self.memory).add_message(query)
        response = pipeline.execute_query(query, thread_id)
        return response
            
pipeline = RagPipeline()
response = pipeline.handle_conversation()
print('---------------DONE----------------------')
        


# queries = [
#     "what is latest dividend declared by the infosys",
#     "write essay on cow",
#     "what happend chandola talav (ahemedabad) on 29 april 2025 give me all details about it",
#     "how many letters in ABCD"
# ]
# query = "what is latest dividend declared by the infosys"
# query = "what is current temperature of the deesa(Gujarat)"
# query = "what happend chandola talav (ahemedabad) on 29 april 2025 give me all details about it"


  


