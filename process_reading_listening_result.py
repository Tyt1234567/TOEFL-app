from docx import Document
import os
from datetime import datetime

def generate_rl_result(user_name,reading_user,reading_answer,l1_user,l1_answer,l2_user,l2_answer):
    reading_correct = 0
    listening_correct = 0
    for index, user_choice in enumerate(reading_user):
        if user_choice == reading_answer[index]:
            reading_correct += 1

    for index, user_choice in enumerate(l1_user):
        if user_choice == l1_answer[index]:
            listening_correct += 1

    for index, user_choice in enumerate(l2_user):
        if user_choice == l2_answer[index]:
            listening_correct += 1

    if reading_correct == 20:
        reading_score = 30
    if reading_correct == 19:
        reading_score = 29
    if reading_correct == 18:
        reading_score = 27
    if reading_correct == 17:
        reading_score = 25
    if reading_correct == 16:
        reading_score = 24
    if reading_correct == 15:
        reading_score = 23
    if reading_correct == 14:
        reading_score = 21
    if reading_correct == 13:
        reading_score = 20
    if reading_correct == 12:
        reading_score = 18
    if reading_correct == 11:
        reading_score = 17
    if reading_correct == 10:
        reading_score = 15
    if reading_correct == 9:
        reading_score = 14
    if reading_correct == 8:
        reading_score = 12
    if reading_correct == 7:
        reading_score = 10
    if reading_correct == 6:
        reading_score = 8
    if reading_correct == 5:
        reading_score = 6
    if reading_correct == 4:
        reading_score = 4
    if reading_correct == 3:
        reading_score = 2
    if reading_correct == 2:
        reading_score = 1
    if reading_correct == 1:
        reading_score = 0
    if reading_correct == 0:
        reading_score = 0

    if listening_correct == 28:
        listening_score = 30
    if listening_correct == 27:
        listening_score = 29
    if listening_correct == 26:
        listening_score = 27
    if listening_correct == 25:
        listening_score = 25
    if listening_correct == 24:
        listening_score = 24
    if listening_correct == 23:
        listening_score = 23
    if listening_correct == 22:
        listening_score = 22
    if listening_correct == 21:
        listening_score = 21
    if listening_correct == 20:
        listening_score = 19
    if listening_correct == 19:
        listening_score = 18
    if listening_correct == 18:
        listening_score = 17
    if listening_correct == 17:
        listening_score = 16
    if listening_correct == 16:
        listening_score = 14
    if listening_correct == 15:
        listening_score = 13
    if listening_correct == 14:
        listening_score = 12
    if listening_correct == 13:
        listening_score = 10
    if listening_correct == 12:
        listening_score = 9
    if listening_correct == 11:
        listening_score = 7
    if listening_correct == 10:
        listening_score = 6
    if listening_correct == 9:
        listening_score = 5
    if listening_correct == 8:
        listening_score = 3
    if listening_correct == 7:
        listening_score = 2
    if listening_correct == 6:
        listening_score = 1
    if listening_correct == 5:
        listening_score = 1
    if listening_correct <= 4:
        listening_score = 0

    time = datetime.now().strftime('%Y-%m-%d')
    file_path = rf'results/{user_name}/{time}/result.doc'
    if os.path.exists(file_path):
        os.remove(file_path)
    doc = Document()
    text_content = ''
    text_content += f'Reading:{reading_score}'
    text_content += '\n'
    text_content += f'listening:{listening_score}'
    text_content += '\n'
    text_content += '\n'
    for i, choice in enumerate(reading_user):
        if choice == reading_answer[i]:
            whether_true = 'True'
        else:
            whether_true = 'False'


        line = f'Reading 第{i+1}题 您的答案：{choice} 正确答案{reading_answer[i]}  对错{whether_true}'
        text_content += line
        text_content += '\n'
    text_content += '\n'

    for i, choice in enumerate(l1_user):
        if choice == l1_answer[i]:
            whether_true = 'True'
        else:
            whether_true = 'False'


        line = f'Listening1 第{i+1}题 您的答案：{choice} 正确答案{l1_answer[i]}  对错{whether_true}'
        text_content += line
        text_content += '\n'

    for i, choice in enumerate(l2_user):
        if choice == l2_answer[i]:
            whether_true = 'True'
        else:
            whether_true = 'False'

        line = f'Listening2 第{i+1}题 您的答案：{choice} 正确答案{l2_answer[i]}  对错{whether_true}'
        text_content += line
        text_content += '\n'

    # 添加文本到文档
    doc.add_paragraph(text_content)
    # 保存文档
    doc.save(file_path)

    return reading_score, listening_score


