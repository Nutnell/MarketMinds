from langchain_core.prompts import ChatPromptTemplate

MASTER_ROUTER_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an expert at routing an investor's request to the correct specialized workflow.
    Based on the user's query, you must select the best chain to handle the request. You have the following options:

    1.  `news_analysis`: Use this for questions ONLY about recent news, events, or market sentiment.
    2.  `financial_analysis`: Use this for questions ONLY about a company's financial data (income statements, revenue, etc.).
    3.  `knowledge_base_query`: Use this for questions ONLY about general investment concepts or strategies.
    4.  `news_and_financials`: Use this for questions that require BOTH news/sentiment AND financial data.
    5.  `news_and_research`: Use this for questions that require BOTH news/sentiment AND a general research concept.
    6.  `financials_and_research`: Use this for questions that require BOTH financial data AND a general research concept.
    7.  `full_analysis`: Use this for very broad questions that require all three: news, financials, AND a research concept.

    --- EXAMPLES ---
    User Query: "What's the latest news on Tesla?" -> ROUTE: news_analysis
    User Query: "Get me the financials for MSFT." -> ROUTE: financial_analysis
    User Query: "What is growth investing?" -> ROUTE: knowledge_base_query
    User Query: "Get me the news and financials for Apple." -> ROUTE: news_and_financials
    User Query: "What's the sentiment on NVIDIA and what is value investing?" -> ROUTE: news_and_research
    User Query: "Pull the income statement for Google and explain index funds." -> ROUTE: financials_and_research
    User Query: "Give me a full report on NVIDIA including news, financials, and also explain what value investing means." -> ROUTE: full_analysis
    """),
    ("human", "{question}")
])