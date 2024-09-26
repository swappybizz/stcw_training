import streamlit as st
from openai import OpenAI
import json
# STCW sections
stcw_sections = [
    "Basic Fire Fighting",
    "Personal Survival Techniques",
    "Elementary First Aid",
    "Personal Safety and Social Responsibilities",
    "Security Awareness Training",
    "life at sea",
]
# Initialize session state variables
if "current_question_answer" not in st.session_state:
    st.session_state.current_question_answer = {}
if "score" not in st.session_state:
    st.session_state.score = 0
if "total_score" not in st.session_state:
    st.session_state.total_score = 0
if "question_history" not in st.session_state:
    st.session_state.question_history = []
if "user_answers" not in st.session_state:
    st.session_state.user_answers = []
if "quiz_over" not in st.session_state:
    st.session_state.quiz_over = False



def fetch_nextQuestion(stcw_section, history):
    system_prompt = """
    You are STCW Examiner. You generate multiple choice questions to test the knowledge of the user on the STCW sections.
    You will focus on {stcw_section} section.
    Respond only in valid JSON format.
    """
    user_prompt = """
    You are provided with a STCW section and a chat history. You are required to only ask about the STCW section.
    Your job is to to genrate next question based on the chat history and the user query.
    
    ###
    Chat History: {history}
    ###
    randomly arrange the options.
    options need to be  tricky with partially correct solution, fully correct solution, a solution that is close but not correct, and a solution that is completely wrong.
    the marks for each option should be out of 10. for correct: 10, partially correct: 5, close but not correct: 0, completely wrong: 0.
    use the following JSON format:
    {{
        "MainQuestion": "..a followup question or new question with increasing difficulty and specificity, if last question qas correct else , easier and more general",
        "Option1": {{ "Content": "...option1", "score": out of 10 }},
        "Option2": "..option2",
        "Option3": "..option3",
        "Option4": "..option4",
    }}
    Reply with only the JSON format.
    Do not include the question number in the JSON format.
    
    """
    model = "gpt-4o"
    client = OpenAI(api_key=st.secrets["openai_api_key"])
    completion = client.chat.completions.create(
        model="gpt-4o",
        response_format = {"type": "json_object"},
        messages=[
                    {
                        "role":"system",
                        "content": system_prompt
                    },
                    {
                        "role":"user",
                        "content": user_prompt
                    },
                ]
    )
    res = completion.choices[0].message.content
    response = json.loads(res)
    # print(f"Response: {response}")
    if response:
        main_question = response["MainQuestion"]
        option1_txt = response["Option1"]["Content"]
        option2_txt = response["Option2"]["Content"]
        option3_txt = response["Option3"]["Content"]
        option4_txt = response["Option4"]["Content"]
        
        option1_score = response["Option1"]["score"]
        option2_score = response["Option2"]["score"]
        option3_score = response["Option3"]["score"]
        option4_score = response["Option4"]["score"]
        return main_question, option1_txt, option2_txt, option3_txt, option4_txt, option1_score, option2_score, option3_score, option4_score
    
    


st.title("STCW Training Mock Test")

#sidebar for user to select the STCW section
st.sidebar.title("Select STCW Section")
selected_section = st.sidebar.selectbox("Select STCW Section", stcw_sections)
st.session_state.selected_section = selected_section
st.session_state.quiz_over = False
st.session_state.score = 0
st.session_state.total_score = 0
st.session_state.question_history = []
st.session_state.user_answers = []

#display current score
st.sidebar.markdown(f"**Current Score:** {st.session_state.score}/{st.session_state.total_score}")

if not st.session_state.quiz_over:
    #fetch the next question
    main_question, option1_txt, option2_txt, option3_txt, option4_txt, option1_score, option2_score, option3_score, option4_score = fetch_nextQuestion(selected_section, st.session_state.question_history)
    st.session_state.current_question_answer = {
        "main_question": main_question,
        "option1": option1_txt,
        "option2": option2_txt,
        "option3": option3_txt,
        "option4": option4_txt,
        "option1_score": option1_score,
        "option2_score": option2_score,
        "option3_score": option3_score,
        "option4_score": option4_score
    }
    st.session_state.total_score += 10
    st.write(main_question)
    st.write("A) " + option1_txt)
    st.write("B) " + option2_txt)
    st.write("C) " + option3_txt)
    st.write("D) " + option4_txt)
    st.session_state.question_history.append(main_question)
    st.session_state.quiz_over = True
    
#user selects the answer
with st.form(key="answer_form"):
    user_answer = st.radio("Select the correct Answer", ["A", "B", "C", "D"])   
    
    if st.form_submit_button("Submit Answer"):
        st.session_state.user_answers.append(user_answer)
        if user_answer == "A":
            user_score = st.session_state.current_question_answer["option1_score"]
        elif user_answer == "B":
            user_score = st.session_state.current_question_answer["option2_score"]
        elif user_answer == "C":
            user_score = st.session_state.current_question_answer["option3_score"]
        elif user_answer == "D":
            user_score = st.session_state.current_question_answer["option4_score"]
        st.session_state.score += user_score
        st.session_state.quiz_over = False
        # fetch the next question
        main_question, option1_txt, option2_txt, option3_txt, option4_txt, option1_score, option2_score, option3_score, option4_score = fetch_nextQuestion(user_answer, selected_section, st.session_state.question_history)
        # make the new question as the current question
        st.session_state.current_question_answer = {
            "main_question": main_question,
            "option1": option1_txt,
            "option2": option2_txt,
            "option3": option3_txt,
            "option4": option4_txt,
            "option1_score": option1_score,
            "option2_score": option2_score,
            "option3_score": option3_score,
            "option4_score": option4_score
        }
    