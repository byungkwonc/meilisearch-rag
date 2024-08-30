import streamlit as st
import meilisearch
from openai import OpenAI
import os
from dotenv import load_dotenv

# .env 파일의 환경 변수를 로드
load_dotenv()

# .env 파일에서 변수 가져오기
master_key = os.getenv('MASTER_KEY')

# 검색엔진 API 키 설정
meili = meilisearch.Client('http://localhost:7700', master_key)

# OPENAI 서비스 키 설정
gpt = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(layout="wide")
col1, col2 = st.columns(2, gap="small")

with col1:
    st.title('검색기')
    search = st.form('search')
    sentence = search.text_input('검색어 입력')
    submit = search.form_submit_button(f'검색!')
    if submit:
        #search(query: str, opt_params: Mapping[str, Any] | None = None)→ Dict[str, Any]
        res = meili.index('girlgroup').search(
            '"'+sentence+'"',
            # {
            #     'hybrid': {
            #         'semanticRatio': 0.5,
            #         'embedder': 'default'
            #     }
            # }
        )

        l = res['hits'][:10]
        for i in l:
            st.title(i['title'])
            st.subheader(i['id'])
            st.markdown(i['text'].replace(sentence, f":red[{sentence}]") )
            st.write('---')

with col2:

    st.title("ChatGPT - 챗봇 🤖")
    on = st.toggle('RAG 활성화')
    if on:
        st.write(':rocket: :red[RAG 작동!]')

    def getMessage():
        messages = []
        template = """Answer the question based only on the following context:
{context}

Question: {question}
"""

        if( on ) :
        	#챗봇에 물어보는 문장을 직접 넣으면 검색엔진이 못찾아서 그냥 첫단어만 짤라서 넣음
            #나중에 벡터검색을 활용해서 hybrid_search 로 변경하면 전체 넣어도 됨
            qq = prompt.split(' ', 1)[0]
            res = meili.index('girlgroup').search(qq)
            context = res['hits'][0]['text']
            q = template.format(context=context, question=prompt)
            messages.append({"role": "user", "content": q})
        else:
            for message in st.session_state.messages:
                messages.append({"role": message["role"], "content": message["content"]})

        return messages

    if "openai_model" not in st.session_state:
        st.session_state["openai_model"] = "gpt-3.5-turbo"

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("What is up?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            print(st.session_state.messages)
            stream = gpt.chat.completions.create(
                model=st.session_state["openai_model"],
                messages=getMessage(),
                stream=True,
            )
            response = st.write_stream(stream)
        st.session_state.messages.append({"role": "assistant", "content": response})