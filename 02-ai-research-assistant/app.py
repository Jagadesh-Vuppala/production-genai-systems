from dotenv import load_dotenv
from pydantic import BaseModel,Field
from typing import List

load_dotenv()


class ResearchResponce(BaseModel):
    answer: str = Field(description="Comprehensive and accurate answer to the research question.")
    confidence: float = Field(ge=0,le=1,description="Confidence score between 0.0 and 1.0 based strictly on source text.")
    sources: List[str] = Field(description="Exact document sections or source tags used.")
    suggestions: List[str] = Field(description="2-3 logical follow-up research questions.")


from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

research_papers = [
    Document(
        page_content="The Transformer architecture relies entirely on an attention mechanism to draw global dependencies between input and output, eschewing recurrence and convolutions entirely. The Multi-Head Attention allows the model to jointly attend to information from different representation subspaces at different positions.",
        metadata={"source": "Attention Is All You Need", "section": "3.2 Multi-Head Attention"}
    ),
    Document(
        page_content="Scaled Dot-Product Attention computes attention as: Attention(Q, K, V) = softmax((Q * K^T) / sqrt(d_k)) * V. The scaling factor of 1 / sqrt(d_k) prevents the dot products from growing excessively large for large dimensions, which would push the softmax into regions with tiny gradients.",
        metadata={"source": "Attention Is All You Need", "section": "3.2.1 Scaled Dot-Product Attention"}
    ),
    Document(
        page_content="Positional Encoding is added to the input embeddings at the bottoms of the encoder and decoder stacks to inject sequence order, since the model contains no recurrence and no convolution. Sinusoidal functions of different frequencies are utilized for this purpose.",
        metadata={"source": "Attention Is All You Need", "section": "3.5 Positional Encoding"}
    )
]

chunks = RecursiveCharacterTextSplitter(chunk_size=1000,chunk_overlap=200).split_documents(research_papers)
retriever = Chroma.from_documents(chunks,OpenAIEmbeddings(model="text-embedding-3-small")).as_retriever(search_kwargs={"k":2})



from langchain_openai import ChatOpenAI
from langchain_classic.retrievers import MultiQueryRetriever, ContextualCompressionRetriever
from langchain_classic.retrievers.document_compressors import LLMChainExtractor

cleaner_llm = ChatOpenAI(model="gpt-5.4-mini-2026-03-17", temperature=0)
multi_query = MultiQueryRetriever.from_llm(retriever=retriever, llm=cleaner_llm)
compressor =  LLMChainExtractor.from_llm(cleaner_llm)
advanced_retriever = ContextualCompressionRetriever(base_compressor=compressor,base_retriever=multi_query)


from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import SQLChatMessageHistory


thinker_llm = ChatOpenAI(model="gpt-6-astra")
structured_thinker = thinker_llm.with_structured_output(ResearchResponce)


research_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert AI Research Scientist. Answer questions strictly based on the following verified context. If the answer is not in the context, set confidence to 0.0.\n\nContext:\n{context}"),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{question}")
])

def format_docs(docs):
    return "\n\n".join(f"[{d.metadata.get('source')} - {d.metadata.get('section')}]: {d.page_content}" for d in docs)

core_chain = (

    # Shortcut:
RunnablePassthrough.assign(
    context=lambda x: format_docs(advanced_retriever.invoke(x["question"]))
)

    | research_prompt
    |structured_thinker
)

def get_session_history(session_id: str):
    return SQLChatMessageHistory(session_id=session_id, connection="sqlite:///research_vault.db")

research_assistant = RunnableWithMessageHistory(
    runnable=core_chain,
    get_session_history=get_session_history,
    input_messages_key="question",
    history_messages_key="history"
)

# ----------------------------------------------------
# 5. Live Research Assistant Execution Block
# ----------------------------------------------------
config = {"configurable": {"session_id": "transformer_deep_dive"}}

questions = [
    "What is the mathematical formula for Scaled Dot-Product Attention and why do we scale it?",
    "How does the model handle word order without recurrence?",
    "What did this paper say about training a Convolutional Neural Network on ImageNet?"
]

print("\n" + "="*60)
print(">>> AI RESEARCH ASSISTANT (gpt-6-astra + gpt-5.4-mini) ONLINE")
print("="*60)

for i, q in enumerate(questions, 1):
    print(f"\n[RESEARCH QUERY {i}]: {q}")
    res = research_assistant.invoke({"question": q}, config=config)
    
    print(f"--> ANSWER:\n{res.answer}")
    print(f"--> SOURCES: {res.sources}")
    print(f"--> CONFIDENCE: {res.confidence}")
    print(f"--> SUGGESTED FOLLOW-UPS: {res.suggestions}")
    print("-" * 60)
