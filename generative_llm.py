from langchain.prompts import PromptTemplate
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.llms import CTransformers
from langchain.chains import RetrievalQA
import asyncio
from fastapi import FastAPI, Request, Response
from hypercorn.asyncio import serve
from hypercorn.config import Config
from starlette.responses import JSONResponse

config = Config()
config.bind = ["localhost:8888"]
app = FastAPI()

DB_FAISS_PATH = 'vectorstore/db_faiss_2'

custom_prompt_template = """Use the following pieces of information to answer the user's question.
If you don't know the answer, just say that you don't know, don't try to make up an answer.

Context: {context}
Question: {question}

Only return the helpful answer below and nothing else.
Helpful answer:
"""

users = dict()

def set_custom_prompt():
    """
    Prompt template for QA retrieval for each vectorstore
    """
    prompt = PromptTemplate(template=custom_prompt_template,
                            input_variables=['context', 'question'])
    return prompt

#Retrieval QA Chain
def retrieval_qa_chain(llm, prompt, db):
    qa_chain = RetrievalQA.from_chain_type(llm=llm,
                                       chain_type='stuff',
                                       retriever=db.as_retriever(search_kwargs={'k': 2}),
                                       return_source_documents=True,
                                       chain_type_kwargs={'prompt': prompt}
                                       )
    return qa_chain

#Loading the model
def load_llm():
    # Load the locally downloaded model here
    llm = CTransformers(
        model="TheBloke/Llama-2-7B-Chat-GGML",
        model_type="llama",
        # max_new_tokens=1024,
        config={'max_new_tokens': 512, 'context_length': 1024},
        temperature=0.5,
        verbose=True
    )
    return llm

#QA Model Function
def qa_bot():
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2",
                                       model_kwargs={'device': 'cpu'})
    db = FAISS.load_local(DB_FAISS_PATH, embeddings, allow_dangerous_deserialization=True)
    llm = load_llm()
    qa_prompt = set_custom_prompt()
    qa = retrieval_qa_chain(llm, qa_prompt, db)

    return qa

#output function
def final_result(query):
    qa_result = qa_bot()
    response = qa_result({'query': query})
    return response

chain = qa_bot()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/message")
async def root(request: Request):
    data = await request.json()
    user_id = data["user_id"]

    if user_id not in users.keys():
        users[user_id] = {'history': None}

    user_info = data["user_info"]
    message = data['message']
    message_to_llm = " ".join([user_info, message])
    print("Message to LLM ---> ", message_to_llm)

    res = await chain.ainvoke(input={'query': message_to_llm})
    answer = res["result"]
    sources = res["source_documents"]
    print('Response from LLM ---> ', answer)

    return JSONResponse(content={'status': 200, 'response': answer})

asyncio.run(serve(app, config))
