# RA-KT-metacognition-and-conginition-training
A streamlit app to solve assignments and get performance feedback.

## Blogpost:
https://dibyanshuchatterjee.com/ra-kt

## RA-KT (Reflection Assistant-Knowledge Tracing) is a tool that has two primary objectives: 
- Train Learners to develop metacognition while they try to solve cognitive (assignments, quizzes etc) loads.

- Give personalized performance metrics to the educators/education providers, to better understand learner’s metacognitive and cognitive performances.

## Input:
- Historical student assingment data.
- Required attributes: student_id, skill_name, correctness, question_text.
- Other required attributes for BKT fitting.

## Output:
- skill mastery percentage (per question answered)
- student's awareness (KMA) and outlook (KMB) (per question answered)


## app.py:

The app.py module hosts the streamlit app code which implements BKT (using pyBKT) to trace student's cognition and Knowledge Monitoring Accuracy (KMA) and Knowledge Monitoring Bias (KMB) to trace student's metacognition. 

## RA-KT Usage:

1.
   ![Screenshot 2024-07-14 at 9 28 47 PM](https://github.com/user-attachments/assets/d70541af-a7b6-47c9-83e8-f35f2bcf9d13)
2.
   ![Screenshot 2024-07-14 at 9 30 25 PM](https://github.com/user-attachments/assets/6554fea9-927f-4fe1-a04c-188e3d656a07)
3.
   ![Screenshot 2024-07-14 at 9 33 10 PM](https://github.com/user-attachments/assets/b994c0e8-89b1-458d-b44f-9420b2aad17b)
4.
   ![Screenshot 2024-07-14 at 9 47 23 PM](https://github.com/user-attachments/assets/3113ad31-6bb9-400c-88a6-247b4afeacca)




