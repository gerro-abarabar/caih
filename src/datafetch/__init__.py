import json
import os
from json import dump, dumps
from typing import List

from datafetch.exam_model import Exam, Question, QuestionList
from datafetch.explanation_model import Lesson

from .prompting import chat_with_ai, explain_exam, get_exam_from_ai, remake_explanation


class DataFetcher:
    messages = {}

    def __init__(self):
        pass

    def fetch_exam(self, questions=5, subject=""):
        return get_exam_from_ai(questions=questions, subject=subject)

    def create_lesson(self, exam: Exam):
        return explain_exam(exam)

    def save_lesson(self, lesson: Lesson, lesson_name: str = ""):
        i = 0
        while True:
            if lesson_name not in os.listdir("./saved_lessons"):
                lesson_name = f"{lesson_name}_{i}"
                break
            i += 1
        lesson.saved = True

        with open(f"./saved_lessons/{lesson_name}.json", "w") as f:
            dump(lesson.model_dump(), f, indent=4)

    def get_lessons(self):
        return os.listdir("./saved_lessons/")

    def get_lesson(self, lesson_name: str = ""):
        with open(f"./saved_lessons/{lesson_name}", "r") as f:
            return Lesson(**json.load(f))

    def remake_explanation(self, question: Question):
        return remake_explanation(question)

    def send_message(self, question, message, system_prompt=None):
        if question.id not in self.messages:
            self.messages[question.id] = []
        if system_prompt is not None and len(self.messages[question.id]) == 0:
            self.messages[question.id].append(
                {"role": "system", "content": system_prompt}
            )
            self.messages[question.id].append(
                {
                    "role": "system",
                    "content": "The question you will discuss is: "
                    + dumps(question.model_dump()),
                }
            )
        self.messages[question.id].append({"role": "user", "content": message})

        response = chat_with_ai(self.messages[question.id])
        return response
