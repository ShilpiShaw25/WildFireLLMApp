from openai import OpenAI
import os
import streamlit as st
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from pinecone import Pinecone


# keys
os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
os.environ["PINECONE_API_KEY"] = st.secrets["PINECONE_API_KEY"]
os.environ["INDEX_HOST"] = st.secrets["INDEX_HOST"]

# constants
NAMESPACE_KEY = "Avijay"
TEXT_MODEL = "text-embedding-ada-002"
QA_MODEL = "gpt-3.5-turbo"
COMMON_TEMPLATE = """
"Please provide information, statistics, and analysis related specifically to wildfires in the {country}. Focus on historical data, current trends, causes, and impacts on the environment and communities. Exclude any information that is not directly related to wildfires in the USA."
"Use the following pieces of context to predict the wildfire risk based on the environmental data at the end with human readable answer as a paragraph."
"Please interpret why you came up with sunc answer in human readbale format."
"don't try to make up an answer. "
"\n\n"
{context}
"\n\n"
Question: {question}
"n"
"Helpful answer:   "
"""


# pinecone setup
pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])
index = pc.Index(host=os.environ["INDEX_HOST"])

# create client
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])


def get_openai_embeddings(text: str) -> list[float]:
    response = client.embeddings.create(input=f"{text}", model=TEXT_MODEL)

    return response.data[0].embedding


# function query similar chunks
def query_response(query_embedding, k = 2, namespace_ = NAMESPACE_KEY):
    query_response = index.query(
        namespace=namespace_,
        vector=query_embedding,
        top_k=k,
        include_values=False,
        include_metadata=True,
    )

    return query_response


def content_extractor(similar_data):
    top_values = similar_data["matches"]
    # get the text out
    text_content = [sub_content["metadata"]["text"] for sub_content in top_values]
    return " ".join(text_content)


def get_model():
    model = ChatOpenAI(model=QA_MODEL, api_key=os.environ["OPENAI_API_KEY"])
    return model


def question_answering(query_question: str, context_text: str, country: str,  template: str = COMMON_TEMPLATE):
    prompt = ChatPromptTemplate.from_template(template)
    model = get_model()
    output_parser = StrOutputParser()

    # create the chain
    chain = prompt | model | output_parser

    # get the answer
    answer = chain.invoke({"country": country,"context": context_text, "question": query_question})

    return answer


def generate_answer(question: str, selected_country: str) -> str:
    # get the query embeddings
    quer_embed_data = get_openai_embeddings(question)

    # query the similar chunks
    similar_chunks = query_response(quer_embed_data)

    # extract the similar text data
    similar_content = content_extractor(similar_chunks)

    # get the answer
    answer = question_answering(question, similar_content, selected_country)

    return answer