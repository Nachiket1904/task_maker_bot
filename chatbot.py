import streamlit as st
import os
from dotenv import load_dotenv
import together
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Load environment variables from .env file
load_dotenv()

# Load Together API key from environment variables
together_api_key = os.getenv('TOGETHER_API_KEY')

# Assume the Together API and other setup are correctly initialized
together.api_key = together_api_key
model = "mistralai/Mixtral-8x7B-Instruct-v0.1"

# Initialize session state for task list if it doesn't exist
if 'tasks' not in st.session_state:
    st.session_state['tasks'] = []

# Streamlit App Layout
st.title("SmartBot - Your Multifaceted Assistant")

# Input field for the user's query
user_query = st.text_input("How can I assist you today?", help="Ask me anything or give me a task.")
default_system_prompt = """You are a task planning and motivation chatbot here to assist me with organizing my tasks and staying motivated. I will tell you about the tasks I need to plan, my preferences for tackling these tasks, and if you're seeking any specific motivation or advice."""

# Function to get chat response and add tasks to to-do list
def get_chat_response_and_update_tasks(query, preferences):
    # Building the prompt with the default system prompt and user's query and details
    prompt = f"{default_system_prompt}\n\nI have the following tasks to complete: {query}. My preferences are: {preferences}. Can you create a plan for me and give me some motivation? Make sure to start the response with 'Your task list is following:'.\n\n"
    output = together.Complete.create(
        prompt=prompt,
        model=model,
        max_tokens=1024,
        temperature=0.7,
        top_k=50,
        top_p=0.7,
        repetition_penalty=1,
        stop=["\\\\</s\\\\>"]  # Corrected the stop sequence
    )
    response = output['output']['choices'][0]['text'].strip()
    
    # Parse the response for tasks and add them to the to-do list
    if response.startswith("Your task list is following:"):
        tasks_str = response.split("Your task list is following:")[1].strip()
        tasks = tasks_str.split("\n")  # Assuming each task is on a new line
        for task in tasks:
            if task:  # Ensure it's not just an empty line
                st.session_state['tasks'].append(task)
        return "Tasks added to your to-do list."
    else:
        return response

# Function to delete a task from the to-do list
def delete_task(task_idx):
    st.session_state['tasks'].pop(task_idx)

# Function to send email to user
def send_email(subject, body, recipient_email):
    sender_email = "" # add your mail
    sender_password = "" #add your password
    # Setup the MIME
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = recipient_email
    message['Subject'] = subject

    # Body and attachments for the mail
    message.attach(MIMEText(body, 'plain'))

    # Create SMTP session for sending the mail
    session = smtplib.SMTP('smtp.gmail.com', 587)  # use gmail with port
    session.starttls()  # enable security
    session.login(sender_email, sender_password)  # login with mail_id and password
    text = message.as_string()
    session.sendmail(sender_email, recipient_email, text)
    session.quit()

# Check if a user query has been entered
if user_query:
    # Input field for the user's preferences
    preferences = st.text_input("Please enter your preferences for completing these tasks:", key="preferences")
    recipient_email = st.text_input("Enter your email address to receive the response:")

    # Button to handle the query after preferences are entered
    if st.button("Submit"):
        response = get_chat_response_and_update_tasks(user_query, preferences)
        st.write(response)
        # Assuming you want to send the response as an email     
        send_email("SmartBot Response", response, recipient_email)

# Display tasks
if st.session_state['tasks']:
    st.write("Your To-Do List:")
    for idx, task in enumerate(st.session_state['tasks']):
        st.write(f"{idx + 1}. {task}")