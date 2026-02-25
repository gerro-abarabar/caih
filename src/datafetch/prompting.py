# This is where they can grab data for prompting.

import json,os
from random import choice
from ollama import Client

def load_exam(file_path="assets"):
    file_path = os.path.join(file_path)
    while True:
        file = choice(os.listdir(file_path))
        if file.endswith(".json"):
            break
    
    with open(os.path.join(file_path, file), "r") as f:
        data = json.load(f)
    return data

def get_exam_from_ai():
    client = Client()
    exam = load_exam()
    messages = [
    {
        'role': 'user',
        'content': 'Create 5 questions just like the following text, also include an explanation why a wrong answer is wrong, and likewise: ' + str(exam[0:4]),
    },
    ]
    messages = client.chat('gpt-oss:120b-cloud', messages=messages, stream=False)
    message=messages.message.content.strip("`")[3:] # TODO: json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)
    print(message)
    return json.loads(message)

def explain_exam(exam):
    client = Client()
    messages = [
    {
        'role': 'user',
        'content': 'Explain the following exam, ignore the json format, just focus on giving the best explanation: ' + str(exam),
    },
    ]
    messages = client.chat('gpt-oss:120b-cloud', messages=messages, stream=False)
    return messages.message.content.strip("`")



if __name__ == "__main__":
    print(load_exam()[0])