import streamlit as st
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import pytesseract
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt

# App Configuration
st.set_page_config(page_title="Your Friendly Math Tutor", layout="wide")
st.title("Your Friendly Math Tutor")

# Sidebar for API Key
openai_api_key = st.sidebar.text_input('OpenAI API Key', type='password')

# Initialize Search History
if 'history' not in st.session_state:
    st.session_state['history'] = []

# Prompt Template
prompt = """
Act as a tutor that helps students solve math and arithmetic reasoning questions.
Students will ask you questions. Think step-by-step to reach the answer. Write down each reasoning step.
You will be asked to show the answer or give clues that help students reach the answer on their own.

Here are a few example questions with expected answers and clues:
Question: What is 5 + 7?
Answer: The sum of 5 and 7 is 12.
Clues: Start by adding the ones place.

Question: {question}
"""

@st.cache_data(show_spinner=False)
def generate_response(question, api_key):
    """Generate a response from the OpenAI chat model."""
    if not api_key:
        return "Error: No API key provided."
    
    try:
        chat = ChatOpenAI(temperature=0.0, openai_api_key=api_key)
        prompt_template = ChatPromptTemplate.from_template(template=prompt)
        messages = prompt_template.format_messages(question=question)
        response = chat.invoke(messages)
        return response.content
    except Exception as e:
        return f"Error: {e}"

# Tesseract OCR Setup (Path to Tesseract executable)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Sidebar Navigation
selected_page = st.sidebar.radio("Navigation", ["Welcome", "Math Tutor", "Graph Plotter"])

# Welcome Page
if selected_page == "Welcome":
    st.header("Welcome to Your Friendly Math Tutor!")
    st.subheader("A smart assistant to help you solve math problems and plot graphs.")
    st.markdown(
        """
        ### Features:
        - Upload an image of a math problem and extract text using OCR.
        - Get step-by-step solutions or helpful clues for math questions.
        - Plot mathematical functions easily.

        *Get started by selecting a page from the navigation menu on the left!*
        """
    )

# Math Tutor Section
elif selected_page == "Math Tutor":
    st.header("Math Tutor")
    with st.form('math_tutor_form'):
        # Image upload widget
        uploaded_image = st.file_uploader("Or upload an image with a math problem", type=['jpg', 'jpeg', 'png'])
        
        # If an image is uploaded, use OCR to extract text
        if uploaded_image:
            image = Image.open(uploaded_image)
            extracted_text = pytesseract.image_to_string(image)
            st.write("Extracted Text from Image:")
            st.info(extracted_text)
            question = extracted_text if extracted_text else "No text found in the image."
        else:
            question = st.text_input('Enter your question:', '')

        action = st.radio('What do you need?', ['Give me clues', 'Show me the answer'], index=0)
        submitted = st.form_submit_button('Submit')

        if submitted:
            if not openai_api_key.startswith('sk-'):
                st.warning('Please enter a valid OpenAI API key!', icon='⚠')
            elif not question.strip():
                st.warning('Please enter a question to proceed!', icon='⚠')
            else:
                response = generate_response(question, openai_api_key)

                if "Clues" in response:
                    clues = response.split("Clues:")[1].strip() if "Clues:" in response else "Clues not provided."
                    answer = response.split("Clues:")[0].strip() if "Clues:" in response else response.strip()

                    if action == 'Give me clues':
                        st.success(f"Clues: {clues}")
                        st.session_state['history'].append({'Question': question, 'Response': clues, 'Type': 'Clues'})
                    else:
                        st.success(f"Answer: {answer}")
                        st.session_state['history'].append({'Question': question, 'Response': answer, 'Type': 'Answer'})
                else:
                    st.error(f"Unexpected response format: {response}. Please try again.")

# Graph Plotter Section
elif selected_page == "Graph Plotter":
    st.header("Graph Plotter")
    st.write("Enter function in the form of y=f(x) (e.g., y=2*x+3):")
    func = st.text_input("Function to plot:", "y=x**2")
    submitted = st.button("Plot")

    if submitted:
        try:
            x = np.linspace(-10, 10, 500)
            y = eval(func.split('=')[1])  # Evaluate the function
            fig, ax = plt.subplots()
            ax.plot(x, y, label=func)
            ax.axhline(0, color='black', linewidth=0.5)
            ax.axvline(0, color='black', linewidth=0.5)
            ax.grid(color='gray', linestyle='--', linewidth=0.5)
            ax.legend()
            st.pyplot(fig)
        except Exception as e:
            st.error(f"Error plotting graph: {e}")

# Display Search History
st.sidebar.header('Search History')
if st.session_state['history']:
    for idx, entry in enumerate(reversed(st.session_state['history'][-5:])):
        st.sidebar.write(f"{entry['Type']} - {entry['Question']}: {entry['Response']}")
else:
    st.sidebar.write("No search history available.")

# Clear History Button
if st.sidebar.button('Clear History'):
    st.session_state['history'] = []
    st.sidebar.success('History cleared!')

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("Made by group 7")