from langchain_core.prompts import ChatPromptTemplate

CONDENSE_QUESTION_PROMPT = ChatPromptTemplate.from_template(
    """Given the following conversation and a follow up question, rephrase the follow up question to be a standalone question.

Chat History:
{chat_history}

Follow Up Input: {question}
Standalone question:"""
)


SIMPLE_RAG_PROMPT = ChatPromptTemplate.from_template(
    """Answer the user's question based only on the following context. If the context does not contain the answer, state that the information is not available in the knowledge base.

    Context: {context}
    Question: {question}

    Helpful Answer:"""
)
