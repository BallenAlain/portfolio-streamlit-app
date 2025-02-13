import streamlit as st
import google.generativeai as genai

MODEL_NAME = "models/gemini-1.5-flash"
with open("system_instruction.txt", 'r') as file:
    SYSTEM_INSTRUCTION=file.read()
sample_prompts = ["Who is Alain?", "What are Alain's skills?", "Tell me about Alain's projects?", "Tell me about Alain's industry experience?"]

st.title("Jim, The Virtual Assistant")

generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 40,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}

def configure_gemini():
    """Configure the generative AI model."""
    genai.configure(api_key=st.secrets["GEMINI_KEY"])
    model = genai.GenerativeModel(model_name=MODEL_NAME, generation_config=generation_config, system_instruction=SYSTEM_INSTRUCTION)
    return model.start_chat(history=[])

def handle_user_prompt(prompt):
    # display user message in chat message container
    with st.chat_message("user", avatar="🐸"):
        st.markdown(prompt)
    # add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt, "avatar": "🐸"})

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        chat = configure_gemini()
        
        output = chat.send_message(prompt, stream=True)
        response = ""
        for chunk in output:
            response += chunk.text
            message_placeholder.markdown(response + "┃ ") # typing animation effect
        
        message_placeholder.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})


# initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
# initialize pill selection state
if "pill_selected" not in st.session_state:
    st.session_state.pill_selected = False

# inital greeting
if not st.session_state.messages:
    greeting = "Hi there! 👋 I'm Jim, an AI virtual assistant. Ask me any questions about Alain."
    st.session_state.messages.append({"role": "assistant", "content": greeting})

# display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar=message.get("avatar", None)):
        st.markdown(message["content"])

# Display pills if none selected and update state on pill selection
if not st.session_state.get("pill_selected"):
    selected_pill = st.pills("Quick questions:", sample_prompts, selection_mode="single")
    if selected_pill:
        st.session_state.pill_selected = True
        handle_user_prompt(selected_pill)
        st.rerun()

# React to user input
if prompt:=st.chat_input("Message Jim!"):
    st.session_state.pill_selected = True
    handle_user_prompt(prompt)
    