import streamlit as st
import pandas as pd
from pyBKT.models import Model
from tabulate import tabulate
from sqlalchemy.sql import text
from sqlalchemy import create_engine, select, MetaData, Table, and_
from pyBKT.models import *



st.set_page_config(
    page_title="RAKT-Student cognition and metacognition tracing",
    page_icon="📝",
)

conn = st.connection('transactions_db', type='sql', url='sqlite:///transactions.db')
engine = create_engine("sqlite:///transactions.db")


@st.cache(allow_output_mutation=True)
def persist_data():
    return {"question": [], "skill": [], "confidence": [], "answer": [], "grade": [], "float_grade": []}


def get_question_text(df, skill_name, assingment, question_text):
    filtered_questions = df.loc[df[skill_name] == assingment, question_text]    
    return filtered_questions

def _process_grades(grade_str):      
    numerator, denominator = grade_str.split("/")
    numerator = float(numerator)
    denominator = float(denominator)
    
    if numerator / denominator >= 0.7:
        result = 1
    else:
        result = 0
    
    return result, numerator/denominator

def calculate_kma(confidence_correctness):

    kma_list = []
    
    for i in range(0, len(confidence_correctness)):
        FC = PC = FI = 0
        temp_list = confidence_correctness[:i+1]

        # Calculate counts for each question up to n
        for idx, c_c in enumerate(temp_list):
            if c_c[2] >= 0.6 and c_c[2] < 0.7:
                ans = 0.5
            elif c_c[2] > 0.7:
                ans = 1
            else:
                ans = 0 
            # ans = c_c[1]
            conf = c_c[0]
            
            if conf == ':rainbow[Partially Confident]':
                conf = 'P'
            elif conf == ':rainbow[Confident]':
                conf = 'C'
            else:
                conf = 'I'
                
            if ans == 1:
                if conf == 'C':
                    FC+=1
                elif conf == 'P':
                    PC+=1
                else:
                    FI+=1
            elif ans == 0.5:
                if conf == 'C':
                    PC+=1
                elif conf == 'P':
                    FC+=1
                else:
                    PC+=1
            else:
                if conf == 'C':
                    FI+=1
                elif conf == 'P':
                    PC+=1
                else:
                    FC+=1
                    
        kma = round((FC - 0.5 * PC - FI) / (FC+PC+FI), 4)
        kma_list.append(kma)

    return kma_list

def calculate_kmb(confidence_correctness):
    kmb_list = []
    
    for i in range(0, len(confidence_correctness)):
        NB = PPB = FPB = POB = FOB = 0
        temp_list = confidence_correctness[:i+1]

        # Calculate counts for each question up to n
        for c_c in temp_list:
            if c_c[2] >= 0.6 and c_c[2] < 0.7:
                ans = 0.5
            elif c_c[2] > 0.7:
                ans = 1
            else:
                ans = 0 
            # ans = idx[1]
            conf = c_c[0]
            
            if conf == ':rainbow[Partially Confident]':
                conf = 'P'
            elif conf == ':rainbow[Confident]':
                conf = 'C'
            else:
                conf = 'I'
                
                
            if ans == 1:
                if conf == 'C':
                    NB+=1
                elif conf == 'P':
                    PPB+=1
                else:
                    FPB+=1
            elif ans == 0.5:
                if conf == 'C':
                    POB+=1
                elif conf == 'P':
                    NB+=1
                else:
                    PPB+=1
            else:
                if conf == 'C':
                    FOB+=1
                elif conf == 'P':
                    POB+=1
                else:
                    NB+=1
                
        # Calculate KMB
        kmb = round((FOB + 0.5 * (POB - PPB) - FPB) / (FOB + POB + NB + PPB + FPB), 4)
        kmb_list.append(kmb)
    return kmb_list







uploaded_data_cols = []
df = pd.DataFrame()

with st.sidebar:
    st.subheader("Upload student dataset")
    csv_data = st.file_uploader(
        "Upload your dataset in CSV format here", accept_multiple_files=False)

    user_id = st.sidebar.text_input('Type the column name corresponding to user_id')
    skill_name = st.sidebar.text_input('Type the column name corresponding to skill_name')
    correct = st.sidebar.text_input('Type the column name corresponding to correct')
    question_text = st.sidebar.text_input('Type the column name corresponding to question_text')
    user_id = user_id.strip()
    skill_name = skill_name.strip()
    correct = correct.strip()
    question_text = question_text.strip()
    

    


    if st.button("Save"):
        with st.spinner("Processing.. "):
            data = pd.read_csv(csv_data)
            data.to_csv("./runtime/runtime_data.csv")


st.header("Enter assingment/skill name to solve questions from")
assingment = st.text_input("Enter name:")
assingment = assingment.strip()

if assingment:
    df = pd.read_csv("./runtime/runtime_data.csv")
    questions = get_question_text(df, skill_name, assingment, question_text)
    question_list = questions.to_list()
    data_dict = persist_data()

    for i, question in enumerate(question_list):
        st.write(f"Question {i + 1}: {question}")
        confidence_input = st.radio(f"Rate your confidence for solving problem {i+1}", 
                                    [":rainbow[Confident]", ":rainbow[Partially Confident]", ":rainbow[Not Confident]"])
        answer_input = st.text_input(f"Answer for Question {i + 1}")
        if answer_input:
            grade = st.text_input(f"Enter grade {i+1}: (format: given_grade/total)")

            if st.button(f"Submit solution and grade {i+1}"):
                data_dict["question"].append(question)
                data_dict["skill"].append(assingment)
                data_dict["confidence"].append(confidence_input)
                data_dict["answer"].append(answer_input)
                data_dict["grade"].append(_process_grades(grade_str=grade)[0])
                data_dict["float_grade"].append(_process_grades(grade_str=grade)[1])
                st.success("Answer and grade submitted!")

            
    if st.button("Fit BKT"):

        df = pd.DataFrame(data_dict)
        with conn.session as s:
            s.execute(text('CREATE TABLE IF NOT EXISTS student_transactions_V4 (question TEXT, skill TEXT, confidence TEXT, answer TEXT, grade INTEGER, float_grade DOUBLE);'))
            s.execute(text('DELETE FROM student_transactions_V4;'))
            for index, row in df.iterrows():                
                s.execute(
                    text('INSERT INTO student_transactions_V4 (question, skill, confidence, answer, grade, float_grade) VALUES (:question, :skill, :confidence, :answer, :grade, :float_grade);'),
                    params=dict(question=row["question"], skill=row["skill"], confidence=row["confidence"], answer=row["answer"], grade=row["grade"], float_grade=row["float_grade"])
                )
            s.commit()
        st.write("Responses Saved. Training model now...")
        
        model = Model(seed = 42, num_fits = 1, parallel = True)

        data = pd.read_csv("./runtime/runtime_data.csv")

        # df = data.copy()
        if not data[correct].isin([0, 1]).all():
            data[correct] = data[correct].map({True: 1, False: 0}).fillna(-1)

        defaults = {'user_id': user_id, 'skill_name': skill_name, 'correct': correct}
        model.fit(data=data, defaults=defaults, skills = assingment)
        training_acc = model.evaluate(data = data, metric = 'accuracy')
        st.write(f"BKT model's accuracy: {training_acc}")
        roster = Roster(students = ['Anonomous'], skills = assingment, model = model)
        
        sql = "select * from student_transactions_V4"
        df = pd.read_sql(sql,con=engine)
        confidence_correctness = list(zip(df['confidence'], df['grade'], df['float_grade']))
        kma = calculate_kma(confidence_correctness)
        kmb = calculate_kmb(confidence_correctness)
        
        # Get KMA calssifications
        kma_classes = []
        for k in kma:
            if k >= -1 and k < -0.25:
                kma_classes.append("LOW")
            elif k >= -0.25 and k < 0.25:
                kma_classes.append("AVERAGE")
            elif k >= 0.25 and k < 0.5:
                kma_classes.append("AVERAGE")
            else:
                kma_classes.append("HIGH")
                
        # Get KMB calssifications
        kmb_classes = []
        for k in kmb:
            if k >= -1 and k < -0.25:
                kmb_classes.append("PESSIMISTIC")
            elif k >= -0.25 and k < 0.25:
                kmb_classes.append("RANDOM")
            elif k >= 0.25 and k < 0.5:
                kmb_classes.append("OPTIMISTIC")
            else:
                kmb_classes.append("OPTEMISTIC")
                
        initial_prob = roster.get_mastery_prob(assingment, 'Anonomous')
        st.write(f"Probability of student's mastery before they took up the assingment: {initial_prob}")

        
        mastery_probs = []
        
        for index, row in df.iterrows(): 
            grade_i = row["grade"]
            new_state = roster.update_state(assingment, 'Anonomous', grade_i)
            prob = roster.get_mastery_prob(assingment, 'Anonomous')
            mastery_probs.append(prob)
                
        df['awareness'] = kma
        df['outlook'] = kmb
        df['awareness_class'] = kma_classes
        df['outlook_class'] = kmb_classes
        df['mastery'] = mastery_probs
        
        st.write(df)





    
    






            


            
    