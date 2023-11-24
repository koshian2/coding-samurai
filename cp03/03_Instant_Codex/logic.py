from typing import Any, Tuple
from PyPDF2 import PdfReader
from langchain.chains import RetrievalQA
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Qdrant
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
import streamlit as st
import asyncio
import os
import requests
import tempfile
import json
import base64

def reset_messsages():
    st.session_state["messages_en"] = []
    st.session_state["messages_jp"] = []

def initialize_state():
    st.session_state["lang"] = "jp"
    st.session_state["paper_url"] = ""
    reset_messsages()

async def download_pdf(url: str):
    if "arxiv.org/abs" in url:
        url = url.replace("/abs/", "/pdf/")
        url += ".pdf"
    original_name = os.path.basename(url)
    fp = tempfile.NamedTemporaryFile(delete=False)

    r = requests.get(url, stream=True)
    for chunk in r.iter_content():
        if chunk:
            fp.write(chunk)
            fp.flush()
    fp.close()

    return fp.name, original_name

async def parse_pdf(paper_url: str) -> Any:
    temp_filename, collection_name = await download_pdf(paper_url)
    pdf_reader = PdfReader(temp_filename)
    text = '\n\n'.join([page.extract_text() for page in pdf_reader.pages])
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        separators=["\n\n"],
        chunk_size=512,
        chunk_overlap=128,
    )
    pdf_text = text_splitter.split_text(text)

    client = QdrantClient(":memory:")
    collection_names = [collection.name for collection in client.get_collections().collections]
    if collection_name in collection_names:
        client.delete_collection(collection_name)

    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
    )    
    qdrant = Qdrant(
        client=client,
        collection_name=collection_name,
        embeddings=OpenAIEmbeddings())
    qdrant.add_texts(pdf_text)
    retriever = qdrant.as_retriever(
        search_type="similarity",
        search_kwargs={"k":4}
    )
    os.remove(temp_filename)
    return retriever

async def create_chains(retriever: Any,
                        use_streaming: bool):
    llm_qa = ChatOpenAI(model="gpt-3.5-turbo-16k-0613", temperature=0.2, 
                        max_tokens=256, streaming=False)
    qa_chain = RetrievalQA.from_chain_type(
            llm=llm_qa,
            chain_type="stuff", 
            retriever=retriever,
            return_source_documents=True)
    translate_llm = ChatOpenAI(model="gpt-3.5-turbo-0613", temperature=0.2, 
                               max_tokens=1024, streaming=use_streaming)
    translate_prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template("与えられた英語を日本語に翻訳してください"),
        HumanMessagePromptTemplate.from_template("{input}")
    ])
    return qa_chain, translate_llm, translate_prompt

async def run_retrieval_chain(chain: RetrievalQA,
                              question: str,
                              update_ui: bool) -> str:
    answer = (await chain.acall(question))["result"]
    if update_ui:
        with st.chat_message("assistant"):
            st.markdown(answer)
    return answer

async def run_translate_chain(llm: ChatOpenAI,
                              prompt_template: ChatPromptTemplate,
                              original_sentence: str,
                              streaming_update_ui: bool) -> str:
    prompt = prompt_template.format_prompt(input=original_sentence)
    
    if streaming_update_ui:
        with st.chat_message("assistant"):
            container = st.empty()
    answer = ""

    async for chunk in llm.astream(prompt):
        answer += chunk.content
        if streaming_update_ui:
            container.markdown(answer)
    
    return answer

async def task_factory(qa_args: Tuple[RetrievalQA, str, bool],
                       translate_args: Tuple[ChatOpenAI, ChatPromptTemplate, str, bool],
                       question_en: str, question_jp: str):
    update_ui_on_qa = qa_args[-1] if qa_args is not None else False
    # Question (EN)
    if qa_args is not None and update_ui_on_qa:
        with st.chat_message("user"):
            st.markdown(question_en)

    # qa and translate
    ans_en, ans_jp = None, None
    if qa_args is not None and translate_args is not None:
        task_qa = asyncio.create_task(run_retrieval_chain(*qa_args))
        task_translate = asyncio.create_task(run_translate_chain(*translate_args))
        ans_en, ans_jp = await asyncio.gather(task_qa, task_translate)
    elif qa_args is not None and translate_args is None:
        ans_en = await run_retrieval_chain(*qa_args)
    elif qa_args is None and translate_args is not None:
        ans_jp = await run_translate_chain(*translate_args)

    # add qa to states
    state_items = [
        ["en", "user", question_en],
        ["jp", "user", question_jp],
        ["en", "assistant", ans_en],
        ["jp", "assistant", ans_jp]
    ]
    for lang, role, content in state_items:
        if content is not None:
            st.session_state[f"messages_{lang}"].append({
                "role": role,
                "content": content
            })

    # Question (JP)
    if qa_args is not None and not update_ui_on_qa:
        with st.chat_message("user"):
            st.markdown(question_jp)

    return ans_en, ans_jp

async def run_summarize(paper_url: str):
    # template questions
    questions = [
        ["What is this paper about?", "この論文はどんなもの？"],
        ["What's so great about it compared to previous research?", "先行研究と比べてどこがすごい？"],
        ["What is the key to the technique or method?", "技術や手法のキモはどこ？"],
        ["How does it validate the proposed method?", "提案手法はどうやって有効だと検証した？"],
        ["Is there any discussion of this paper?", "この論文に対する議論はある？"],
        ["What paper should I read next to better understand this paper?", "この論文をより深く理解する上で次に読むべき論文は何？"]
    ]

    # reset message states
    reset_messsages()
    st.session_state["paper_url"] = paper_url

    # create chains
    retriever = await parse_pdf(paper_url)
    qa_chain, translate_llm, translate_prompt = await create_chains(
        retriever=retriever, 
        use_streaming=st.session_state["lang"]=="jp")
    
    # args
    ans_en, ans_jp = None, None
    for i in range(len(questions)+1):
        qa_args, translate_args = None, None
        q_item = questions[i] if i < len(questions) else [None, None]
        if i < len(questions):
            qa_args = (qa_chain, questions[i][0], st.session_state["lang"]=="en")
        if i >= 1:
            translate_args = (translate_llm, translate_prompt, ans_en, st.session_state["lang"]=="jp")
        ans_en, ans_jp = await task_factory(qa_args, translate_args, *q_item)

def get_download_injection_html():
    data = {
        "messages_en": st.session_state["messages_en"],
        "messages_jp": st.session_state["messages_jp"],
        "paper_url": st.session_state["paper_url"]
    }
    json_str = json.dumps(data, ensure_ascii=False, indent=4, separators=(',', ': '))
    json_str = base64.b64encode(json_str.encode()).decode()

    download_link = f"data:file/plain;base64,{json_str}"
    download_filename = f"{os.path.basename(st.session_state['paper_url'])}.json"
    injection_html = f"""
<a id="download-link" href="{download_link}" download="{download_filename}" style="display: none">
    Download link
</a>
<script>
    document.getElementById('download-link').click();
</script>"""
    return injection_html