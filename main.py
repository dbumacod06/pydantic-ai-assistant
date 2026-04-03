from pydantic_ai import ModelMessage
import streamlit as st
from pydantic_agent import schedulerAgent


def main() -> None:
    '''Runs the Streamlit application for the Virtual Assistant.'''
    st.set_page_config(page_title="Streamlit Chatbot", page_icon="🤖")
    st.title("Dhoby The Great's Personal Assistant")
    
    if "messages" not in st.session_state:
        st.session_state.messages: List[ModelMessage] = []

    # Display Chat Messages from History
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Handle User Input
    if prompt := st.chat_input("How can I be of service milord?"):
        with st.chat_message("user"):
            st.markdown(prompt)
        
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("assistant"):
            result = schedulerAgent.run_sync(prompt, message_history=st.session_state.messages)
            assistantResponse = result.output
            st.write(assistantResponse)
        
        # Add assistant response to session state
        st.session_state.messages.extend(result.new_messages())


if __name__ == "__main__":
    main()