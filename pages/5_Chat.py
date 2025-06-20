import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage

st.set_page_config(layout="wide")
st.title("In development. Coming soon...")
st.subheader("🤖 Ask me about your data")
st.write("Ask me anything about your data! I will use AI to try to help you and give you some insights. For example:")
st.markdown("- Do you see any pattern in my data?")
st.markdown("- Is my weight loss optimal?")
st.markdown("- How much time it will take to reach my goal weight?")
st.markdown('''
            <style>
            [data-testid="stMarkdownContainer"] ul{
                padding-left:40px;
            }
            </style>
            ''', unsafe_allow_html=True)

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    
# Display chat messages from history
for message in st.session_state.messages:
    if isinstance(message, HumanMessage):
        with st.chat_message("user"):
            st.markdown(message.content)
    elif isinstance(message, AIMessage):
        with st.chat_message("assistant"):
            st.markdown(message.content)
    

# User input
prompt = st.chat_input("Write your question here...")

# Generate response
if prompt:
    with st.chat_message("user"):
        st.markdown(prompt)
        st.session_state.messages.append(HumanMessage(content=prompt))
        
    with st.chat_message("assistant"):
        message = "Hello! How can I help you?"
        st.markdown(message)
        st.session_state.messages.append(AIMessage(content=message))
        