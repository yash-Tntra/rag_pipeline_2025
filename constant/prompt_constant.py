ROUTE_SELECTOR = """
        Analyze the following user query: {} and determine if it requires retrieval from external knowledge
        sources (e.g., facts, real-world data, references) or if it can be answered directly using internal language
         understanding and reasoning.


        If the query requires retrieval of factual or external knowledge, return exactly:
        "Rag"
        If the query can be answered using general reasoning, understanding, or creative generation without external
        facts, return exactly:
        "LLM"
        Do not include any explanations, additional text, or formatting or quotes. The response must strictly be either
        "Rag" or "LLM".
        """
