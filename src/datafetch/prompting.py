import json
import os
import re
from math import ceil
from random import choice, randint
from time import sleep
from typing import List

from ollama import Client

from .exam_model import Exam, Question, QuestionList
from .explanation_model import Lesson


def load_exam(file_path="assets", subject=""):
    path = os.path.join(file_path, subject.lower())
    # Ensure directory exists to avoid infinite loops
    if not os.path.exists(path):
        os.makedirs(path)

    files = [f for f in os.listdir(path) if f.endswith(".json")]
    if not files:
        raise FileNotFoundError(f"No .json files found in {path}")

    file = choice(files)  # Picks a random json file
    with open(os.path.join(path, file), "r", encoding="utf-8") as f:
        return json.load(f)


def get_random_cuts(questions) -> list[int]:
    """
    Returns a list of random numbers that add up to the number of questions
    """
    cuts: list[int] = []
    max_cuts = ceil(questions / 3)  # Cut into three parts
    while sum(cuts) < questions:
        cut = randint(1, max_cuts)
        cuts.append(cut)
    return cuts


def get_exam_from_ai(questions, subject):
    client = Client()
    cuts = get_random_cuts(questions)
    example_json = []  # The example the AI must referenec
    image_list = []  # used for giving the AI the image
    formatted_images = {}  # Used to retrieve the image by assigning names
    for cut in cuts:
        exam_json = load_exam(subject=subject)
        start_number = randint(0, len(exam_json) - cut - 1)
        exam = exam_json[start_number : start_number + cut]
        if any(
            "images" in question for question in exam
        ):  # Imports the image if it exists and removes it to save space
            for question in exam:
                if question.get("images", []):
                    # This gets the dict of images
                    images = question.get("images")

                    # Replace the images with their names
                    question["images"] = list(images.keys())

                    # Adds to the list of used images
                    image_list.append(*images.values())
                    formatted_images.update(images)
                    print(type(question.get("images")))
        example_json.append(exam)
    print(cuts)
    # We only need a slice for context
    # print(example_json)
    # print(json.dumps(example_json))

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
                f"\n\n### REFERENCE EXAMPLE:\n{json.dumps(example_json)}"  # FIXME: Problem with Json things
                "\n\n### STRICT RULES:"
                "\n1. The 'id' must start at 1 and increment sequentially."
                "\n2. 'correct_answer' must be the choice id of the correct answer."
                "\n3. Map descriptions to the provided images accurately."
                "\n4. Return ONLY the raw JSON."
                "\n5. Put the data of the image in the 'images' key where it was referenced."
                "\n6. You may not create any new image. Only use the provided ones and use the same name used in the question."
                "\n7. You must use the same name for the image used in the question, you may not use the image data itself."
            ),
            "images": image_list,  # Ensure your Ollama client supports the 'images' key here
        },
    ]  # Thanks Gemini.
    while True:  # Infinite Loop in case AI make mistakes
        final_exam = None
        # Using Gemini 3 Flash for high reliability
        try:
            print("Trying to generate questions...")
            response = client.chat(
                "gemma4:31b-cloud",
                messages=messages,
                stream=False,
                format=Exam.model_json_schema(),
            )
            raw_content = response.message.content
            final_exam = Exam.model_validate_json(fix_content(raw_content))
            final_exam.add_images(formatted_images)
            print(f"Successfully generated {len(final_exam.types)} questions.")
        except Exception as e:
            print(f"Error in generating exam: {e}. Retrying...")
            final_exam = None
            sleep(2)  # To avoid rate limits
        if final_exam:
            break

    return final_exam


def fix_content(content: str) -> str:
    """Fixes the error of something like:
        Invalid JSON: invalid escape at line 109 column 84 [type=json_invalid, input_value='{\n  "subject": "Mathema...n      ]\n    }\n  ]\n}', input_type=str]
    Fixes it by changing the \n to \\n, and also changing the ]\n and }\n to ]\\n and }\\n so that it can be properly parsed by the JSON parser.
    """
    # Unescape newlines
    content = content.replace("\\n", "\n")
    # Fix the list new line
    content = content.replace("]\\n", "]\n")
    # Fix the set new line
    content = content.replace("}\\n", "}\n")
    return content


def explain_exam(exam: List[QuestionList]):
    # Remove images
    # for question in exam: # TODO: Remove images before going into Gemini, then return it like from get_exam_from_ai
    #     if question.get("images", []):
    #         question["images"] = list(question["images"].keys())
    images = {}
    for question_list in exam:
        print(question_list)
        if question_list.has_images():
            images.update(question_list.get_images())
            question_list.remove_images()

    client = Client()
    messages = [
        {
            "role": "system",
            "content": (
                "You are a master educator specializing in academic recovery and curriculum design. "
                "Your goal is to convert exam errors into structured, objective study notes. "
                "Follow these structural principles:\n"
                "1. Logical Mapping: Identify the specific principle violated in each incorrect answer.\n"
                "2. Objective Rectification: Provide a direct, factual bridge between the error and the correct concept.\n"
                "3. Systematic Organization: Present information in a clear, hierarchical format suitable for high-school level review.\n"
                "4. Multi-Modal Synthesis: Integrate visual data from provided images into the logical explanations.\n\n"
                "Output must be strictly raw JSON matching the provided schema."
            ),
        },
        {
            "role": "user",
            "content": (
                f"### EXAM DATA:\n{json.dumps([question_list.model_dump() for question_list in exam])}\n\n"
                "### SUPPLEMENTAL DATA:\n"
                "- Use context from history data.\n"
                "- Incorporate provided mnemonics as technical memory aids.\n\n"
                "### TASK:\n"
                "1. Analyze the exam questions and images to identify core conceptual gaps.\n"
                "2. Formulate a 'core_explanation' that focuses on the objective logic and facts missed by the student.\n"
                "3. Generate a 'similar_exam' with at least 3 new questions that rigorously test the same underlying principles.\n\n"
                f"### SCHEMA:\n{Lesson.model_json_schema()}\n\n"
                "### CONSTRAINTS:\n"
                "- Do not use markdown backticks (```json).\n"
                "- Maintain an objective, academic tone; avoid conversational or entertaining fillers.\n"
                "- Ensure the 'similar_exam' focuses on practical application of the concepts.\n"
                "- Ensure the JSON is valid and mirrors the internal logic of the missed questions."
            ),
            "images": images.values(),
        },
    ]
    while True:  # Infinite Loop in case AI make mistakes
        final_lesson = None
        # Using Gemini 3 Flash for high reliability
        try:
            print("Trying to generate lesson...")
            response = client.chat(
                "gemma4:31b-cloud",
                messages=messages,
                stream=False,
                format=Lesson.model_json_schema(),
            )
            raw_content = response.message.content
            final_lesson = Lesson.model_validate_json(fix_content(raw_content))
            final_lesson.add_images(images)

        except Exception as e:
            print(f"Error in explaining exam: {e}. Retrying...")
            final_lesson = None
            sleep(2)  # To avoid rate limits
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
                "Maintain a strictly objective and neutral tone."
            ),
        },
    ]
    response = client.chat(
        "gemma4:31b-cloud",
        messages=messages,
        stream=False,
        format=Lesson.model_json_schema(),
    )
    return response.message.content


def chat_with_ai(messages: List[dict]):
    client = Client()
    while True:
        try:
            response = client.chat(
                "gemma4:31b-cloud",
                messages=messages,
                stream=True,
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
        new_explanation = explain_exam(new_exam.types)
        print(f"Successfully generated explanation.")
        print(new_explanation)

        # print(json.dumps(new_exam[0], indent=2))
    except Exception as e:
        print(f"Error: {e}")
