import asyncio
import logging
from langchain.chains.conversation.base import ConversationChain
from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain_community.llms.ollama import Ollama
from langchain_core.callbacks import StreamingStdOutCallbackHandler
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import MessagesPlaceholder, HumanMessagePromptTemplate

from web_search_service import WebScrapService
from langchain.memory import ConversationBufferMemory, CombinedMemory
from embedding_vector_store_service import EmbeddingVectorStore
from langchain.retrievers import EnsembleRetriever, ContextualCompressionRetriever
from langchain_community.retrievers import BM25Retriever
from constant.prompt_constant import ROUTE_SELECTOR
from langchain.prompts import ChatPromptTemplate


# from langchain_ollama import OllamaLLM   #todo use later


class RagPipeline:

    def __init__(self):
        self.llm = Ollama(model= "llama3", callbacks=[StreamingStdOutCallbackHandler()], temperature=0.2)
        self.memory = ConversationBufferMemory(
            memory_key="history",
            return_messages=True
        )
        self.qa = ConversationChain(llm=self.llm, memory=self.memory, verbose=True)

    def check_where_to_go(self, prompt):
        finance_query_classification = ROUTE_SELECTOR.format(prompt)
        system_selector = self.llm.invoke(finance_query_classification)
        print(f"prompt is {query} : and selector is {system_selector}")
        return system_selector

    def execute_query(self, prompt):
        keyword = self.check_where_to_go(prompt)
        keyword_executor = {
            "Rag": self.rag_call,
            "LLM": self.llm_call
        }
        return keyword_executor.get(keyword, self.rag_call)(prompt)

    def rag_call(self, query):
        # web scrap module and documents
        documents = asyncio.run(WebScrapService().duckduckgo_search_and_scrape(query))
        vectorstore, bm25_retriever = EmbeddingVectorStore().embedding_vector_store_service(documents)
        retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 2})

        hybrid_retriever = EnsembleRetriever(
                retrievers=[retriever, bm25_retriever],
                weights=[0.3, 0.7]
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
            verbose= True
        )
        response = rag_chain.run(query)
        return response

    def llm_call(self, query):
        result = self.qa.run(query)
        return  result


# queries = [
#     "what is latest dividend declared by the infosys",
#     "write essay on cow",
#     "what happend chandola talav (ahemedabad) on 29 april 2025 give me all details about it",
#     "how many letters in ABCD"
# ]
# query = "what is latest dividend declared by the infosys"
# query = "what is current temperature of the deesa(Gujarat)"
# query = "what happend chandola talav (ahemedabad) on 29 april 2025 give me all details about it"

pipeline = RagPipeline()
while True:
    query = input("human: ")
    # system_message = SystemMessage(content=(
    #     "You are a helpful assistant."
    # ))
    # human_message = HumanMessage(content=(
    #     f"{query}"
    # ))
    #
    prompt_template = ChatPromptTemplate.from_messages([
        HumanMessagePromptTemplate.from_template("{query}")
    ])
    prompt = prompt_template.format(query=query)
        
    response = pipeline.execute_query(prompt)
    print(response)
