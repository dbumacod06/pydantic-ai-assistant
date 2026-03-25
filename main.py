import streamlit as st
from pydantic_agent import scheduler_agent, set_meeting, send_email, MeetingDetails, EmailDetails


def main():
    st.set_page_config(page_title="Streamlit Chatbot", page_icon="🤖")
    st.title("Dhoby The Great's Personal Assistant")
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # 2. Display Chat Messages from History
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 3. Handle User Input
    if prompt := st.chat_input("How can I be of service milord?"):
        with st.chat_message("user"):
            st.markdown(prompt)
        
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("assistant"):
            return_str = ''
            result = scheduler_agent.run_sync(prompt)
            if isinstance(result.output,MeetingDetails):
                meeting_result = set_meeting(result.output)
                print(meeting_result)
                return_str = scheduler_agent.run_sync(f"Tell the user if his meeting was successful based on these details: {meeting_result}").output
            if isinstance(result.output,EmailDetails):
                email_result = send_email(result.output)
                print(email_result)
                return_str = scheduler_agent.run_sync(f"Create a confirmation response based on the email details: {email_result}").output
            if isinstance(result.output,str):
                return_str = result.output
            st.write(return_str)
            print(return_str)
        
        # Add assistant response to session state
        st.session_state.messages.append({"role": "assistant", "content": return_str})


if __name__ == "__main__":
    main()