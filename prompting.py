from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from structure import *
import os
import json

api_key = os.environ.get("GOOGLE_API_KEY")
#initializing model
llm = ChatGoogleGenerativeAI(
    model = 'gemini-2.5-flash',
    temperature = 0,
    google_api_key = api_key,
)

structured_llm = llm.with_structured_output(ExtractedMetrics)

prompt = ChatPromptTemplate([
    ('system',
     '''
     You're an expert sustainability analyst specializing in ESG metrics extraction.
     Extract ALL relevant metrics, targets, and KPIs from the text and format them to the provided schema. 
     '''),
    ("human", '{text_chunk}')
])

def process(docs):
    chain = prompt | structured_llm
    batch_inputs = [{'text_chunk': doc.page_content if hasattr(doc, 'page_content') else doc} for doc in docs]

    results = chain.batch(batch_inputs)
    return results
