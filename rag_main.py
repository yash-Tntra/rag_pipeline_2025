import asyncio

from langchain.chains.conversation.base import ConversationChain
from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain_community.chat_models import ChatOpenAI
from langchain_community.llms.ollama import Ollama
from langchain_core.callbacks import StreamingStdOutCallbackHandler
from config.config import OpenAi
from web_search_service import WebScrapService
from langchain.memory import ConversationBufferMemory, CombinedMemory
from embedding_vector_store_service import EmbeddingVectorStore
from langchain.retrievers import EnsembleRetriever, ContextualCompressionRetriever
# from langchain.retrievers.document_compressors import LLMReranker

from langchain_community.retrievers import BM25Retriever

# from langchain_ollama import OllamaLLM   #todo use later


class RagPipeline:
    
    def __init__(self):
        self.memory = ConversationBufferMemory(memory_key="history", return_messages=True)
        # self.llm = ChatOpenAI(
        #     model_name="gpt-4o",
        #     openai_api_key=OpenAi.OPEN_API_KEY.value,
        #     temperature=0
        # )
        self.llm = Ollama(model= "llama3")
    
    def check_where_to_go(self, prompt):
        finance_query_classification = f"""
        Analyze the following user query: "{prompt}" and determine if it requires retrieval from external knowledge
        sources (e.g., facts, real-world data, references) or if it can be answered directly using internal language
         understanding and reasoning.
        If the query requires retrieval of factual or external knowledge, return exactly:
        "Rag"
        If the query can be answered using general reasoning, understanding, or creative generation without external
        facts, return exactly:
        "LLM"
        Do not include any explanations, additional text, or formatting. The response must strictly be either
        "Rag" or "LLM".
        """
        system_selector = self.llm.invoke(finance_query_classification)
        print(f"prompt is {query} : and selector is {system_selector}")
        return system_selector
    
    def execute_query(self, prompt):
        keyword = self.check_where_to_go(prompt)
        keyword_executor = {
            "Rag": self.rag_call,
            "LLM": self.llm_call
        }
        return keyword_executor[keyword](prompt)
 
    def rag_call(self, query):
        # web scrap module and documents
        documents = asyncio.run(WebScrapService().duckduckgo_search_and_scrape(query))
        vectorstore, bm25_retriever = EmbeddingVectorStore().embedding_vector_store_service(documents)
        retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 2})
        
        hybrid_retriever = EnsembleRetriever(
                retrievers=[retriever, bm25_retriever],
                weights=[0.6, 0.4]
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
            memory=self.memory
        )
        response = rag_chain.run(query)
        return response
    
    def llm_call(self, query):
        qa = ConversationChain(llm=self.llm, memory=self.memory)
        result = qa.run(query)
        return  result
    
    
queries = [
    "what is latest dividend declared by the infosys",
    "write essay on cow",
    "what happend chandola talav (ahemedabad) on 29 april 2025 give me all details about it",
    "how many letters in ABCD"
]
# query = "what is latest dividend declared by the infosys"
# query = "what is current temperature of the deesa(Gujarat)"
# query = "what happend chandola talav (ahemedabad) on 29 april 2025 give me all details about it"
for query in queries:
    response = RagPipeline().execute_query(query)
    print(response)
