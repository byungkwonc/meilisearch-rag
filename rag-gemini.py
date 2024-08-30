import streamlit as st
import meilisearch

import pathlib
import textwrap
import google.generativeai as genai
from IPython.display import display
from IPython.display import Markdown

import os, time
from dotenv import load_dotenv

# .env 파일의 환경 변수를 로드
load_dotenv()
# .env 파일에서 변수 가져오기
master_key = os.getenv('MASTER_KEY')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

def to_markdown(text):
  text = text.replace('•', '  *')
  return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))

# 검색엔진 API 키 설정
meili = meilisearch.Client('http://localhost:7700', master_key)

# Gmini 서비스 키 설정
genai.configure(api_key=GOOGLE_API_KEY)

generation_config = genai.GenerationConfig(
		candidate_count=1,
		stop_sequences=['x'],
		temperature=0.7,
		top_p=0.95,
		#top_k=64,
		max_output_tokens=8192,
		#response_mime_type="application/json"
)

safety_settings=[
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_ONLY_HIGH",
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_ONLY_HIGH",
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_ONLY_HIGH",
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_ONLY_HIGH",
    },
]

MODEL_ROLE = 'ai'
AI_AVATAR_ICON = '✨'

st.set_page_config(layout="wide")
col1, col2 = st.columns(2, gap="small")

with col1:
    st.title('meilisearch 검색기')
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
            #st.title(i['title'])
            st.title(i['title'].replace(sentence, f":red[{sentence}]") )
            st.subheader(i['id'])
            st.markdown(i['text'].replace(sentence, f":red[{sentence}]") )
            #st.markdown(i['overview'].replace(sentence, f":red[{sentence}]") )
            #st.markdown(i['genres'])
            #st.markdown(i['poster'])
            st.write('---')

with col2:
    #model = genai.GenerativeModel('gemini-pro')
    st.session_state.messages = []
    st.session_state.gemini_history = []
    st.session_state.model = genai.GenerativeModel(
        model_name='gemini-1.5-flash',
        generation_config=generation_config,
        safety_settings=safety_settings,
        system_instruction="""
           You are korean. Your name is GGAMNYANG. In Korean, it's "깜냥"."""
    )
    st.session_state.chat = st.session_state.model.start_chat(
        history=st.session_state.gemini_history,
    )
    st.title("Gemini Pro - 챗봇 🤖")
    on = st.toggle('RAG 활성화')
    if on:
        st.write(':rocket: :red[RAG 작동!]')

    def getMessage():
        queries = []
        template = """Answer the question based only on the following context:
{context}

Question: {question}
"""
        if( on ) :
        	#챗봇에 물어보는 문장을 직접 넣으면 검색엔진이 못찾아서 그냥 첫단어만 짤라서 넣음
            #나중에 벡터검색을 활용해서 hybrid_search 로 변경하면 전체 넣어도 됨
            qq = prompt.split(' ', 1)[0]
            res = meili.index('movies').search(qq)
            #context = res['hits'][0]['text']
            context = res['hits'][0]['overview']
            q = template.format(context=context, question=prompt)
            #messages.append(dict(role='user', content=q,))
            queries = q
        else:
            #for message in st.session_state.messages:
            #    messages.append(dict(role=message['role'],content=message['content'],))
            queries = prompt

        print('-'*30)
        print(queries)
        return queries

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(
            name=message['role'],
            avatar=message.get('avatar'),
        ):
            st.markdown(message['content'])

	# React to user input
    if prompt := st.chat_input("What is up?"):
        # Display user message in chat message container
        with st.chat_message('user'):
            st.markdown(prompt)
        # Add user message to chat history
        st.session_state.messages.append(
            dict(
                role='user',
                content=prompt,
            )
        )
        ## Send message to AI
        response = st.session_state.chat.send_message(
            #prompt,
            getMessage(),
            stream=True,
        )
        # Display assistant response in chat message container
        with st.chat_message(
            name=MODEL_ROLE,
            avatar=AI_AVATAR_ICON,
        ):
            message_placeholder = st.empty()
            full_response = ''
            assistant_response = response
            # Streams in a chunk at a time
            for chunk in response:
                # Simulate stream of chunk
                # TODO: Chunk missing `text` if API stops mid-stream ("safety"?)
                for ch in chunk.text.split(' '):
                    full_response += ch + ' '
                    time.sleep(0.05)
                    # Rewrites with a cursor at end
                    message_placeholder.write(full_response + '▌')
            # Write full message with placeholder
            message_placeholder.write(full_response)

        # Add assistant response to chat history
        st.session_state.messages.append(
            dict(
                role=MODEL_ROLE,
                content=st.session_state.chat.history[-1].parts[0].text,
                avatar=AI_AVATAR_ICON,
            )
        )
        print('-'*30)
        print(st.session_state.messages)
        st.session_state.gemini_history = st.session_state.chat.history
        print('-'*30)
        print(st.session_state.gemini_history)
