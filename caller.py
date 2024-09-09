from helper import *
from langchain_community.vectorstores import FAISS

import base64
# import os
# os.environ["HF_TOKEN"] = userdata.get('hugging_face_api_key')# to download the ColPali model
# os.environ["ANTHROPIC_API_KEY"] = userdata.get('ANTHROPIC_API_KEY')
from byaldi import RAGMultiModalModel
from claudette import *
from dotenv import load_dotenv
load_dotenv()

import time
import pickle
def normal_injection():
    start_time = time.time()  # Start the timer

    # File processing
    pages = file_to_chunks("data")

    # Save pages to pickle file
    with open("pages.pkl", "wb") as f:
        pickle.dump(pages, f)

    # Create FAISS database from pages
    db = FAISS.from_documents(pages, OpenAIEmbeddings())
    
    # Save the FAISS database locally
    db.save_local("Normal")

    end_time = time.time()  # End the timer
    total_time = end_time - start_time  # Calculate the total time

    print(f"Time taken to run the function: {total_time} seconds")


import os 
from langchain.docstore.document import Document
def file_to_Raptor_chunks(folder):
    pages=[]
    for file_name in os.listdir(f"{folder}"):
        d=load_file(f"{folder}/{file_name}")
        print(file_name)
        raptor_chunks=recursive_embed_cluster_summarize([p.page_content for p in d], level=1, n_levels=5)
        all_texts = [p.page_content for p in d]
        for level in sorted(raptor_chunks.keys()):
            # Extract summaries from the current level's DataFrame
            summaries = raptor_chunks[level][1]["summaries"].tolist()
            # Extend all_texts with the summaries from the current level
            all_texts.extend(summaries)
        document =  []
        for item in range(len(all_texts)):
            page = Document(page_content=all_texts[item],metadata={"file_name":file_name})
            document.append(page)
        pages.extend(document)
    return pages

import time
import pickle
def raptor_injestion():
    start_time = time.time() 
    d=file_to_Raptor_chunks("data")
    with open("RAPTOR.pkl", "wb") as f:
        pickle.dump(d, f)

    db = FAISS.from_documents(d, OpenAIEmbeddings())
    db.save_local("RAPTOR")
    end_time = time.time()  # End the timer
    total_time = end_time - start_time  # Calculate the total time

    print(f"Time taken to run the function: {total_time} seconds")


from langchain_openai import ChatOpenAI

from langchain_core.runnables import RunnablePassthrough
from langchain import hub


def rag(database_name,Query):
    db=FAISS.load_local(database_name,OpenAIEmbeddings(),allow_dangerous_deserialization=True)
    faiss_retriever=db.as_retriever(search_kwargs={'k': 4})

    llm = ChatOpenAI(model="gpt-4o-mini")
    prompt = hub.pull("rlm/rag-prompt")

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)


    normal_rag_chain = (
        {"context": faiss_retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    return normal_rag_chain.invoke(Query)


def colpali(Query):
    from byaldi import RAGMultiModalModel

    model = RAGMultiModalModel.from_index("attention")
    results = model.search(Query, k=1)
    image_bytes = base64.b64decode(results[0].base64)

    chat = Chat(models[1])
    # models is a claudette helper that contains the list of models available on your account, as of 2024-09-06, [1] is Claude Sonnet 3.5:
    return chat([image_bytes, Query])