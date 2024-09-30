""" 
Steps:
 - 
"""

confidence = ""
grade = ""
initial_mastery = 0

prompt = f"""
Assume your role as  teaching assistant. A student in your class has answered 10 questions from their assingment. 
The professor has provided a detailed feedback of student's performance per question answered, based on the amount of approximate skill they accuired after answering each question, the amount of awareness they possesed of their knowledge of the topic before they answered the question and what was their outlook about themselves being able to solve the problem before they actually attempted solving it.
Based on the feedback provided by the professor, you task is to generate an appropriate intervention that can help the student stay on track and perform well.
Professor's feedback for every solution is within <feedback> </feedback> tag:
<feedback>
    - The student said they were {confidence} and they got the question {grade}.
    - When the student started the assingment, they posseed approximately {initial_mastery} % mastery of the topic.
    - 
"""