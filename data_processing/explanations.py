# This file creates explanations for the json that hadn't got a explanation
from concurrent.futures import ThreadPoolExecutor
import json
import os
import struct
import time
from random import randint
from ollama import Client
from tkinter import filedialog, Tk



def get_file_from_user():
    root = Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
    if not file_path:
        raise ValueError("User must select a file")
    return file_path

def load_exam(file_path="assets"):
    file_path = os.path.join(file_path)
    
    with open(os.path.join(file_path), "r") as f:
        data = json.load(f)
    return data


llm_message=[
    # Math
    "You are an expert STEM Tutor. Analyze this entrance exam question:\n{question}\n\n"
           "Provide a structured derivation using these steps:\n"
           "1. FUNDAMENTAL PRINCIPLE: Identify the core theorem or law required.\n"
           "2. STEP-BY-STEP DERIVATION: Show the logical flow from the question to the answer.\n"
           "3. THE 'EXAM HACK': If there is a dimensional analysis trick, estimation technique, or shortcut to eliminate options quickly, explain it.",
    # Linguistics
    "You are a Verbal Reasoning expert. Analyze this question and its context:\n{question}\n\n"
           "Provide a linguistic breakdown:\n"
           "1. KEYWORD ANALYSIS: Identify the specific words in the prompt that dictate the correct answer.\n"
           "2. LOGICAL JUSTIFICATION: Explain why the correct answer is the most semantically sound.\n"
           "3. DISTRACTOR DECONSTRUCTION: Briefly explain why the most 'tempting' wrong options are incorrect (e.g., too broad, too narrow, or out of context).",
    # General Knowledge
    "You are a General Knowledge expert. Review this exam question:\n{question}\n\n" 
           "Explain the factual basis for the answer:\n"
           "1. HISTORICAL/SCIENTIFIC CONTEXT: Provide the background facts that make this answer true.\n"
           "2. CONCEPTUAL MAPPING: How does this specific fact connect to the broader subject matter?\n"
           "3. MEMORY ANCHOR: Give a mnemonic or a quick 'rule of thumb' to help remember this fact for future questions."
]

def ask_llm(question):
    client=Client()
    response=""
    max_retries = 5
    for _ in range(max_retries):
        try:
            response = client.chat(model_used, 
                messages=[
                    {  
                        "role": "user",
                            "content": llm_message[choice].format(question=json.dumps(question, indent=4))
                        }
                    ]
                    )
            content = response.message.content.strip("`")
            if content: return content

        except Exception as e:
            print(f"Error: {e}. Retrying...")
            time.sleep(randint(5,10))
        return "No explanation available after multiple attempts."

import socket

host = "0.0.0.0"
port = 45612
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def get_full_data(conn):
    # Receiver side
    header = conn.recv(4)
    if header:
        msg_len = int.from_bytes(header, byteorder='big') # Simplified example
        chunks = []
        bytes_recd = 0
        while bytes_recd < msg_len:
            chunk = conn.recv(min(msg_len - bytes_recd, 1024))
            
            if not chunk: break 
            chunks.append(chunk)
            bytes_recd += len(chunk)
        full_msg = b''.join(chunks).decode()
        return full_msg 

def wait_until_complete(batch=10):
    
    data=[]
    while (len(data) < batch):
        conn, address = server_socket.accept()
        
        new_data = get_full_data(conn)
        # data must be a json
        data.append(json.loads(new_data)) 
        
        # Send an acknowledgment back to the client
        message = "Message Received"
        conn.send(message.encode())
        conn.close()
    return data

def handle_data_question(question):
    explanation=""
    while not explanation or explanation.strip() == "No explanation available after multiple attempts.":
        explanation = ask_llm(question)
        question["explanation"] = explanation
    return question

def process_question(model, question):
    """The logic previously in thread_func, now standalone"""
    try:
        # This allows multiple retries to get an explanation if the LLM fails, without crashing the whole process
        if not question.get("explanation") or question["explanation"].strip() == "No explanation available after multiple attempts.":
            # 1. Get LLM result
            updated_q = handle_data_question(question)
        else:
            updated_q = question
        payload = json.dumps(updated_q).encode("utf-8")
        header = struct.pack('>I', len(payload))
        
        # 2. Send to local 'collector' server
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(("127.0.0.1", port))
            s.sendall(header + payload)
            # Short timeout for the ack
            s.settimeout(5.0)
            ack = s.recv(1024).decode()
            return True
    except Exception as e:
        print(f"Failed to process/send question: {e}")
        return False
choice = 0
if __name__ == "__main__":
    exam = load_exam(get_file_from_user())
    
    while choice not in [1, 2, 3]:
        choice = int(input("What type of exam is it?\n"
                "\t1. Reasoning (Math, Logic, etc.)\n"
                "\t2. Language Proficiency (English, etc.)\n"
                "\t3. General Knowledge (History, Science, etc.)"))
        if choice not in [1, 2, 3]:
            print("Invalid choice. Please try again.")

    model_used=['deepseek-v3.2:cloud', 'ministral-3:14b-cloud', 'qwen3.5:397b-cloud'][choice-1]
    print(model_used)
    
    batch_size = 10
    final_data=[]
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen(batch_size)
    with ThreadPoolExecutor(max_workers=5) as executor:
        # This handles the batching correctly even for odd numbers
        for i in range(0, len(exam), batch_size):
            batch = exam[i : i + batch_size]
            
            # Start LLM tasks
            for q in batch:
                executor.submit(process_question, model_used, q)
            
            # Collect results for this batch
            final_data.extend(wait_until_complete(batch=len(batch)))
            print(final_data)
    server_socket.close()
    final_data.sort(key=lambda x: x['id'])
    with open("final_data.json", "w") as f:
        json.dump(final_data, f, indent=4)


