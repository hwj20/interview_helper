import os

import openai
from openai import OpenAI

api_key =  'sk-proj-grnX1j3w4Sk5TZHq4ElCT3BlbkFJtantkkLhYuztkJRyzg27'
# 设置OpenAI API密钥
# openai.api_key = 'sk-proj-grnX1j3w4Sk5TZHq4ElCT3BlbkFJtantkkLhYuztkJRyzg27'
previous_answer = {}
question_number = 0


def generate_reply(question, cv_content="Not provided", job_title="software engineer", job_description="Not Provided",
                   user_name="Wanjing", pronoun="She"):
    prompt = f"""
   Act as an interviewee {user_name}, and {pronoun} are applying for the position of {job_title}
   The job descriptions are: {job_description}.
   The interviewee's CV is:{cv_content}.
   And your previous answers are:{previous_answer}
   """
    user_request = f"Generate a very short answer for this question: {question}"
    try:
        client = OpenAI(
            api_key=api_key,
        )
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": prompt},
                {
                    "role": "user",
                    "content": user_request
                }
            ]
        )

        generated_answer = str(completion.choices[0].message.content)
        print((len(generated_answer)))
        previous_answer[question] = generated_answer
        print(previous_answer)
        return generated_answer
    except Exception as e:
        return f"API调用错误: {e}"


# 0 applicant
# 1 interviewer
# 3 error
def determine_type(content):
    if content == "音频未能识别" or len(content) < 5 or "错误" in content:
        return 3
    prompt = f"""
    You are reading selected words from an interviewing dialog. \
    Return 0 if they are from applicant and 1 if there are any question from interviewer within them.
"""
    user_request = f"Determine whether these words are from answer of applicant or interviewer: {content}"
    try:
        client = OpenAI(
            api_key=api_key,
        )
        # print(os.environ.get("OPENAI_API_KEY"))
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": prompt},
                {
                    "role": "user",
                    "content": user_request
                }
            ]
        )

        role = completion.choices[0].message.content
        # if role == 0:
        #     previous_answer={"applicant"}
        print(role)
        return role
    except Exception as e:
        print(e)
        return 3
