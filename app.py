import os
import streamlit as st
from model import load_agent
from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

agent = load_agent()
st.title("Fitness Bot")

if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = [("You", "Hi"), ("Bot", "How can I help you?")]

with st.sidebar:
    st.subheader("Guidlines")
    guid = st.container(height=200)
    gd = """
    --> Write your instructions clearly mentioning what each number signifies.
    --> While calculating BMI please mention the weight first then the height.
    """
    guid.chat_message("assistant").write("Write your instructions clearly mentioning what each number signifies.")
    guid.chat_message("assistant").write("While calculating BMI please mention the weight first then the height.")

prompt = st.chat_input("Enter your query...")
if prompt:
    response = agent.invoke({
        "input": prompt,
        # "chat_history":[HumanMessage(content=st.session_state['chat_history']["You"]), AIMessage(content=st.session_state['chat_history']['Bot'])]
    })
    with st.chat_message("user"):
        st.write(f"{prompt}")
    st.session_state['chat_history'].append(("You", prompt))

    with st.chat_message("assistant"):
        st.write(response['output'])
    st.session_state['chat_history'].append(("Bot", response['output']))

with st.sidebar:
    st.subheader('History')
    hist = st.container(height=500)
    for role, text in st.session_state['chat_history']:
        if role == "You":
            hist.chat_message("user").write(text)
        else:
            hist.chat_message("assistant").write(text)