import json
import os
from json import dump
from typing import List

from datafetch.exam_model import Question, QuestionList
from datafetch.explanation_model import Lesson

from .prompting import explain_exam, get_exam_from_ai, remake_explanation


class DataFetcher:
    def __init__(self):
        pass

    def fetch_exam(self, questions=5, subject=""):
        return get_exam_from_ai(questions=questions, subject=subject)

    def create_lesson(self, exam: List[QuestionList]):
        return explain_exam(exam)

    def save_lesson(self, lesson: Lesson, lesson_name: str = ""):
        i = 0
        while True:
            if not lesson_name in os.listdir("./saved_lessons"):
                lesson_name = f"{lesson_name}_{i}"
                break
            i += 1
        lesson.saved = True

        with open(f"./saved_lessons/{lesson_name}.json", "w") as f:
            dump(lesson.model_dump(), f, indent=4)

    def get_lessons(self):
        return os.listdir(f"./saved_lessons/")

    def get_lesson(self, lesson_name: str = ""):
        with open(f"./saved_lessons/{lesson_name}", "r") as f:
            return Lesson(**json.load(f))

    def remake_explanation(self, question: Question):
        return remake_explanation(question)
