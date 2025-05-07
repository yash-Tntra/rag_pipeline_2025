import asyncio
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.retrievers import BM25Retriever
from langchain_community.vectorstores import Milvus
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS


class EmbeddingVectorStore:
    def embedding_service(self, docuemnts):
        text_splitter =RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        docs = text_splitter.split_documents(docuemnts)

        # embedding_model_name = "sentence-transformers/all-mpnet-base-v2"
        embedding_model_name= "BAAI/bge-base-en-v1.5"
        model_kwargs = {"device": "cpu"}  # or "cuda" if GPU available
        encode_kwargs = {"normalize_embeddings": True}

        embeddings = HuggingFaceEmbeddings(
            model_name=embedding_model_name,
            model_kwargs=model_kwargs,
            encode_kwargs=encode_kwargs
        )
        # embeddings = OpenAIEmbeddings(openai_api_key=OpenAi.OPEN_API_KEY.value)
        return embeddings, docs

    async def vector_store_service(self, embeddings, docs):
        # vectorstore = Milvus.from_documents(
        #     documents=docs,
        #     embedding=embeddings,
        #     connection_args={
        #         "uri": "./milvus_demo.db",
        #     },
        #     drop_old=True,  # Drop the old Milvus collection if it exists
        # )
        vectorstore_task = asyncio.to_thread(FAISS.from_documents, docs, embeddings)
        bm25_task = asyncio.to_thread(BM25Retriever.from_documents, docs)
        vectorstore, bm25_retriever = await asyncio.gather(vectorstore_task, bm25_task)

        return  vectorstore, bm25_retriever

    def embedding_vector_store_service(self, documents):
        embeddings, docs = self.embedding_service(documents)
        vectorstore, bm25_retriever = asyncio.run(self.vector_store_service(embeddings, docs))
        return vectorstore, bm25_retriever








