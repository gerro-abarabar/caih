# Pydantic Model of what the AI must follow
from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel


class Image(BaseModel):
    description: str
    data: Optional[bytes]
    name: str


class Choice(BaseModel):
    choice: str
    id: str


class Question(BaseModel):
    id: int
    question: str
    choices: List[Choice]
    images: List[Image]
    correct_answer: str
    explanation: str
    answer: Optional[str] = None

    def add_answer(self, answer: str):
        self.answer = answer

    def add_images(self, images: dict):
        for image in self.images:
            if image.name in images.keys():
                image.data = images[image.name]
            else:
                print("cannot find image", image.name)

    def get_choice(self, choice_id) -> Optional[Choice]:

        for choice in self.choices:
            if choice.id == choice_id:
                return choice
        return None

    def has_image(self) -> bool:
        for image in self.images:
            if image.data is not None:
                return True
        return False

    def get_images(self):
        return self.images

    def remove_images(self):
        self.images = []


class QuestionList(BaseModel):
    questions: List[Question]
    instruction: str

    def delete_question(self, question_id):
        try:
            self.questions = [
                question for question in self.questions if question.id != question_id
            ]
        except ValueError:
            pass

    def add_images(self, images: dict):
        for question in self.questions:
            question.add_images(images)

    def add_answer(self, question_id, answer):
        for question in self.questions:
            if question.id == question_id:
                question.add_answer(answer)
                break
        else:
            raise ValueError(f"Question with ID {question_id} not found")

    def has_images(self) -> bool:
        for question in self.questions:
            if question.has_image():
                return True
        return False

    def get_images(self):
        image_dict = {}
        for question in self.questions:
            if images := question.get_images() != []:
                image_dict[images.name] = images  # pyright: ignore[reportAttributeAccessIssue]
        return image_dict

    def remove_image(self, question_id):
        for question in self.questions:
            if question.id == question_id:
                question.remove_images()
                break

    def remove_images(self):
        for question in self.questions:
            question.remove_images()

    def get_question(self, id) -> Optional[Question]:
        for question in self.questions:
            if question.id == id:
                return question


class Exam(BaseModel):
    types: List[QuestionList]
    subject: str
    is_lesson: bool
    taken_at: Optional[str] = None
    score: Optional[int] = None
    saved: bool = False
    subject_folder: Optional[str] = None

    def add_images(self, images: dict):
        for question_list in self.types:
            question_list.add_images(images)

    def has_image(self) -> List[QuestionList]:
        has_images = [
            question_list for question_list in self.types if question_list.has_images()
        ]

        return has_images
