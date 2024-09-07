import sys
import os
import streamlit as st

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# pylint: disable=C0413
from app.scrape import scrape_data

# Initialize session state to store chat history, scraped_data and question
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

if "scraped_data" not in st.session_state:
    st.session_state["scraped_data"] = ""

if "question" not in st.session_state:
    st.session_state["question"] = ""

if "query_submitted" not in st.session_state:
    st.session_state["query_submitted"] = False


# TODO - If needed add this to on_click when `Scrape it` button is clicked
def reset_chat_history():
    """
    Resets the chat history by clearing the session state's chat history list.

    Returns:
        None
    """
    st.session_state["chat_history"] = []


def update_chat_history():
    """
    Updates the chat history by appending a new question and answer pair to the session state.

    Retrieves the current question and scraped data from the session state, generates an answer,
    and appends the question and answer pair to the chat history if both are available.

    Parameters:
        None

    Returns:
        None
    """
    question = st.session_state.question
    context = st.session_state["scraped_data"]
    # TODO - call another function to get the answer
    answer = "Generated answer..."  # Placeholder for actual answer
    if question and answer:
        st.session_state["chat_history"].append((question, answer))


st.title("AI Web Scraper")

url = st.text_input("Enter the URL you want to scrape:")

if st.button("Scrap It"):
    if url:
        scraped_data = scrape_data(url)
        st.session_state["scraped_data"] = scraped_data
        st.success("Site scraped successfully!")
    else:
        st.error("Please enter a valid URL.")

# Display the scraped content if available
if st.session_state["scraped_data"]:
    with st.expander("Scraped Content"):
        st.text_area(
            "Scraped Content",
            value=st.session_state["scraped_data"],
            height=200,
        )

# Q/A Section
if st.session_state["scraped_data"]:
    st.subheader("Q/A Section")

    # Display chat history with copy buttons for each response
    if st.session_state["chat_history"]:
        for index, (q, a) in enumerate(st.session_state["chat_history"]):
            with st.container():
                st.markdown(f"**Q{index + 1}:** {q}")
                st.code(
                    a
                )  # Adding the Copy button functionality using code TODO - need to enhance this
                st.markdown("---")

    # Input for asking questions
    with st.form("my-form", clear_on_submit=True):
        st.text_input("Ask a question based on the scraped content:", key="question")
        submit_button = st.form_submit_button(
            "Submit question", on_click=update_chat_history
        )
        if submit_button:
            st.session_state["query_submitted"] = True

    if st.session_state["query_submitted"]:
        if st.session_state.question:
            st.success("Answer generated!")
        else:
            st.error("Please ask a question.")

        st.session_state["query_submitted"] = False
