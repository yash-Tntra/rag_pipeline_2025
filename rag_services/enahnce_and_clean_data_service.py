from datetime import datetime

class EnhanceService:
    def __init__(self, llm):
        self.llm = llm

    def prompt_enhance_service(self, query):
        prompt = """
        You are a highly intelligent AI assistant. Enhance and expand the following user query by
        identifying the core intent and transforming it into, well-structured prompt suitable for
        a large language model to understand and respond accurately.
        Original User Query:
        "{query}"
        Instructions:
        1. just enhance and clarify the user intent
        2. does not include any extra comment or text or title from your side
        3. Enhance user query if needed if not needed pass as it is (must follow this)
    """
        # """
        #  Instructions:
        # 1. Clarify the intent of the query.
        #  2. Add relevant context or background information, if needed.
        # 3. Transform it into a single, complete prompt for LLM processing.
        # 4. Maintain the user's tone and goal.
        # """

        query = prompt.format(query=query)
        llm_query = self.llm.invoke(query)
        return llm_query


    def clean_urls_data_service(self, doc, query):
        print(f"Started cleaning...")
        current_datetime = datetime.now()

        prompt = f"""
        {query} understand this user query and find the relevant and meaningful data from the
        {doc.page_content} as per the current date time {current_datetime}. Also take care of the cleaning process if you need like remove unnecessary
        spaces and other things. Note: don't add any extra comments or text just give me proper answer
        from your side.
        """

        llm_ans = self.llm.invoke(prompt)
        doc.page_content = llm_ans

        print(f"Completed cleaning... ")
        return doc

    def review_llm_result(self, query, llm_result):
        prompt = """
        You are an expert response validator and enhancer, Your task is to validate and enhancer
        the LLM's response against the original user query.

        Instructions:
        3. Enhance LLM response if needed if not needed to enhance pass as it is and do not enhance it(must follow this)
        2. does not include any extra  or unnecessary comment, text ,tags or titles(Enhanced Response:)
        just provide clean response only from your side(must follow this).
        1. just enhance and clarify the user intent with the llm response and give answer as per conversations

        **Input:**
        User Query:
        "{user_query}"

        LLM Response:
        "{llm_response}"
        """
        # """
        #
        # Follow these steps:
        #
        # 1. **Understand the User Query**: Extract the core intent and context of the user's query.
        # 2. **Validate the LLM's Response**:
        #    - Check if the answer directly addresses the user's question.
        #    - Ensure that the response is factually correct, complete, and relevant.
        #    - Identify any hallucinations, missing context, or off-topic content.
        # 3. **Enhance the Response** (if needed):
        #    - Refine unclear or incomplete parts.
        #    - Add missing context or critical details.
        #    - Improve clarity, tone, and helpfulness.
        # 4. **Format the Output**:
        #    - Present the final version in a clean, structured, and readable format
        #     (bullet points, paragraphs, or code blocks as appropriate).
        # 5. **Major Rule**:
        #     - Enhance LLM response if needed if not needed pass as it is (must follow this)
        # ---
        #
        #   **Output:**
        #
        # - **Is the response aligned with the query intent?** (Yes/No)
        # - **Validation Summary**:
        #   (Brief explanation of the response accuracy, relevance, and completeness)
        # - **Enhanced and Formatted Answer**:
        #   (The improved response, rewritten for clarity and accuracy)
        # - **Corrections (if any)**:
        #   (Note specific errors or misinterpretations)
        # """
        llm_prompt  = prompt.format(user_query=query, llm_response=llm_result)
        result = self.llm.invoke(llm_prompt)
        return result




