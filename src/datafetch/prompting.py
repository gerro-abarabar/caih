import json
import os
from math import ceil
from random import choice, randint
from time import sleep
from typing import List

from ollama import Client

from .exam_model import Exam, Question
from .explanation_model import Lesson

MODEL = "gemma4:31b-cloud"  # Model can be changed manually here


def load_exam(file_path="assets", subject=""):
    path = os.path.join(file_path, subject.lower())
    if not os.path.exists(path):
        os.makedirs(path)

    files = [f for f in os.listdir(path) if f.endswith(".json")]
    if not files:
        raise FileNotFoundError(f"No .json files found in {path}")

    file = choice(files)  # Picks a random json file
    with open(os.path.join(path, file), "r", encoding="utf-8") as f:
        return json.load(f)


def get_random_cuts(questions) -> list[int]:
    cuts: list[int] = []
    max_cuts = ceil(questions / 3)
    while sum(cuts) < questions:
        cut = randint(1, max_cuts)
        cuts.append(cut)
    return cuts


def get_exam_from_ai(questions, subject):
    client = Client()
    cuts = get_random_cuts(questions)
    example_json = []
    image_list = []
    formatted_images = {}
    for cut in cuts:
        exam_json = load_exam(subject=subject)
        start_number = randint(0, len(exam_json) - cut - 1)
        exam = exam_json[start_number : start_number + cut]
        if any("images" in question for question in exam):
            for question in exam:
                if question.get("images", []):
                    images = question.get("images")
                    question["images"] = list(images.keys())
                    image_list.append(*images.values())
                    formatted_images.update(images)
                    print(type(question.get("images")))
        example_json.append(exam)
    print(cuts)

    # Double braces safely escape unexpanded brackets for python f-strings
    formatted_example = json.dumps(example_json).replace("{", "{{").replace("}", "}}")

    messages = [
        {
            "role": "system",
            "content": (
                "You are a pedagogical assistant that generates structured exam data. "
                "Your output must be a single, valid JSON object strictly following the provided schema. "
                "Do not include markdown formatting, backticks (```json), or any text outside the JSON structure. "
                "Ensure all internal string newlines are escaped as '\\n'."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Generate an 'Exam' object containing {questions} new questions. "
                f"\n\n### SCHEMA CONSTRAINTS:\n{Exam.model_json_schema()}"
                f"\n\n### REFERENCE EXAMPLE:\n{formatted_example}"
                "\n\n### STRICT RULES:"
                "\n1. The 'id' must start at 1 and increment sequentially."
                "\n2. 'correct_answer' must be the choice id of the correct answer."
                "\n3. Map descriptions to the provided images accurately."
                "\n4. Return ONLY the raw JSON."
                "\n5. Put the data of the image in the 'images' key where it was referenced."
                "\n6. You may not create any new image. Only use the provided ones and use the same name used in the question."
                "\n7. You must use the same name for the image used in the question, you may not use the image data itself."
                "\n8. Strictly, do not use emojis, no matter how important it is."
            ),
            "images": image_list,
        },
    ]
    while True:
        final_exam = None
        try:
            print("Trying to generate questions...")
            final_response = ""
            response = client.chat(
                MODEL,
                messages=messages,
                format=Exam.model_json_schema(),
                stream=True,
                options={"temperature": 0.2},
            )
            for chunk in response:
                message = chunk.message.content
                final_response += message  # pyright: ignore[reportOperatorIssue]
                print(message, end="", flush=True)

            # Pydantic native validation parses pristine escaped JSON structures perfectly
            final_exam = Exam.model_validate_json(final_response)
            final_exam.add_images(formatted_images)
            final_exam.subject_folder = subject.lower()
            print(f"\nSuccessfully generated {len(final_exam.types)} question types.")

            assert sum(len(type.questions) for type in final_exam.types) >= questions

        except Exception as e:
            print(f"\nError in generating exam: {e}. Retrying...")
            final_exam = None
            sleep(2)
        if final_exam:
            break

    return final_exam


def explain_exam(exam: Exam):
    images = {}
    question_lists = exam.types
    for q_list in question_lists:
        if q_list.has_images():
            images.update(q_list.get_images())
            q_list.remove_images()

    client = Client()
    messages = [
        {
            "role": "system",
            "content": (
                "You are a master educator specializing in academic recovery and curriculum design. "
                "Your goal is to convert exam errors into structured, comprehensive, and exhaustive study notes. "
                "Follow these structural principles:\n"
                "1. Logical Mapping: Identify the specific principle violated in each incorrect answer.\n"
                "2. Objective Rectification: Provide a direct, factual bridge between the error and the correct concept.\n"
                "3. Systematic Organization: Present information in a clear, hierarchical format suitable for high-school level review.\n"
                "4. Multi-Modal Synthesis: Integrate visual data from provided images into the logical explanations.\n\n"
                "Output must be strictly raw JSON matching the provided schema. Internal string newlines must be escaped as '\\n'."
            ),
        },
        {
            "role": "user",
            "content": (
                f"### EXAM DATA:\n{exam.model_dump()}\n\n"
                "### SUPPLEMENTAL DATA:\n"
                "- Use context from history data.\n"
                "- Incorporate provided mnemonics as technical memory aids.\n\n"
                "### TASK:\n"
                "1. Analyze the exam questions and images to identify core conceptual gaps.\n"
                "2. Formulate an exhaustive, deep-dive 'core_explanation' utilizing rich Markdown headers and rigorous LaTeX mathematical symbols for all formulas/equations.\n"
                "3. Generate AT LEAST 10 completely unique study flashcards in the 'memory_aids' list.\n"
                "4. Generate a 'similar_exam' containing AT LEAST 10 highly rigorous new questions testing these exact concepts.\n\n"
                f"### SCHEMA:\n{Lesson.model_json_schema()}\n\n"
                "### STRICTOR CONSTRAINTS:\n"
                "- Do not use markdown backticks (```json) outside the JSON structure.\n"
                "- Maintain an objective, academic tone; avoid conversational or entertaining fillers.\n"
                "- Every question in 'similar_exam' must have its own detailed markdown/LaTeX 'explanation' string matching your STEM/Verbal styles.\n"
                "- Strictly, do not use emojis."
            ),
            "images": list(images.values()),
        },
    ]
    while True:
        final_lesson = None
        try:
            print("Trying to generate lesson...")
            response = client.chat(
                MODEL,
                messages=messages,
                stream=True,
                format=Lesson.model_json_schema(),
                options={
                    "temperature": 0.2,
                    "num_predict": 8192,
                },  # Added token runway for long lessons
            )
            final_response = ""
            for chunk in response:
                message = chunk.message.content
                final_response += message  # FIXED: Now properly appends chunk strings  # pyright: ignore[reportOperatorIssue]
                print(message, end="", flush=True)

            final_lesson = Lesson.model_validate_json(final_response)
            final_lesson.add_images(images)
            final_lesson.similar_exam.subject_folder = exam.subject_folder
            print("\nSuccessfully generated lesson.")
        except Exception as e:
            print(f"\nError in explaining exam: {e}. Retrying...")
            final_lesson = None
            sleep(2)
        if final_lesson:
            break
    return final_lesson


def remake_explanation(question: Question):
    client = Client()
    messages = [
        {
            "role": "system",
            "content": (
                "You are an expert academic tutor. Your task is to rewrite the provided "
                "explanation to maximize clarity, logical progression, and technical accuracy. "
                "Follow these principles:\n"
                "1. Objective Precision: Use formal, academic language. Eliminate all "
                "conversational fillers, anecdotes, or motivational language.\n"
                "2. Logical Sequencing: Present the explanation in a step-by-step "
                "deductive format, ensuring each point leads naturally to the next.\n"
                "3. Fact-Driven: Focus strictly on the underlying principles, definitions, "
                "and evidence required to answer the question.\n"
                "4. Structure: Use clear signposting (e.g., 'Step 1', 'Definition', 'Conclusion') "
                "to organize the text for student notes."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Original question with explanation: {json.dumps(question.model_dump())}\n\n"
                "TASK: Remake the explanation into a formal, structured academic note. "
                "The output must be plain text only. Do not use markdown backticks or JSON formatting. "
                "Maintain a strictly objective and neutral tone. "
                "Strictly, do not use emojis."
            ),
        },
    ]
    response = client.chat(
        MODEL,
        messages=messages,
        stream=False,
        options={"temperature": 0.2},
    )
    return response.message.content


def chat_with_ai(messages: List[dict]):
    client = Client()
    while True:
        try:
            response = client.chat(
                MODEL,
                messages=messages,
                stream=True,
                options={
                    "temperature": 0.2  # Low temperature keeps it strict and adherent to the schema
                },
            )
            return response
        except Exception as e:
            print(f"Error in AI chat: {e}. Retrying...")
            sleep(2)  # To avoid rate limits


if __name__ == "__main__":
    # Test the AI generation
    try:
        new_exam = get_exam_from_ai(questions=5, subject="mathematics")
        # print(f"Successfully generated {len([*question_list.questions for question_list in new_exam.types])} questions.") # Dont use this, this gives an error
        new_explanation = explain_exam(new_exam)
        print("Successfully generated explanation.")
        print(new_explanation)

        # print(json.dumps(new_exam[0], indent=2))
    except Exception as e:
        print(f"Error: {e}")
