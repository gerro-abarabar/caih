# This is the model where the AI would make the explantion in.

from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from .exam_model import Exam, Image


class Mnemonic(BaseModel):
    tool: str = Field(
        ..., description="The acronym, rhyme, or memory trick (e.g., SOH CAH TOA)."
    )
    application: str = Field(
        ...,
        description="A comprehensive, rich-text markdown explanation of how to apply this trick to the specific concept.",
    )
    images: List[Image] = Field(
        ..., description="Images associated with the flashcard."
    )


class Lesson(BaseModel):
    topic_title: str = Field(
        ...,
        description="A clear, comprehensive title for the academic recovery lesson.",
    )

    # ENFORCE DEEP FORMATTING HERE
    core_explanation: str = Field(
        ...,
        description=(
            "An extremely thorough, textbook-style deep dive into the logic, rules, and fundamental principles. "
            "You MUST use extensive rich Markdown formatting (Headers ###, ####, bullet points, bolding, and horizontal rules `---`). "
            "All mathematical derivations, formulas, and expressions MUST be typeset using inline LaTeX ($...$) or block LaTeX ($$...$$). "
            "Do not write flat walls of plain text."
        ),
    )

    historical_context: str = Field(
        ...,
        description="The background, evolutionary origin, or historical development behind this concept.",
    )

    # ENFORCE THE 10 FLASHCARD MINIMUM HERE
    memory_aids: List[Mnemonic] = Field(
        ...,
        description="A comprehensive list containing AT LEAST 10 highly distinct flashcards/mnemonics covering all sub-topics.",
    )

    similar_exam: Exam = Field(
        ...,
        description="A follow-up diagnostic exam containing exactly 10 comprehensive, newly synthesized math/general questions.",
    )
    images: List[Image] = Field(
        ..., description="Images associated with the overall lesson."
    )
    saved: Optional[bool] = False

    def add_images(self, images: Dict[str, Image]):
        for image in self.images:
            if image.name in images.keys():
                image.data = images[image.name].data
            else:
                print("cannot find image", image.name)
