from dataclasses import dataclass
from typing import List

@dataclass
class MBTIQuestion:
    id: int
    content: str
    option_a: str
    option_b: str
    dimension_a: str
    dimension_b: str

@dataclass
class TestQuestion:
    id: int
    content: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    option_e: str
    category: str

class TestGenerator:
    @staticmethod
    def format_mbti_questions(raw_data: List[dict]) -> List[MBTIQuestion]:
        questions = []
        for q in raw_data:
            questions.append(MBTIQuestion(
                id=q['id'],
                content=q['content'],
                option_a=q['option_a'],
                option_b=q['option_b'],
                dimension_a=q['dimension_a'],
                dimension_b=q['dimension_b']
            ))
        return questions

    @staticmethod
    def format_other_questions(raw_data: List[dict]) -> List[TestQuestion]:
        questions = []
        for q in raw_data:
            questions.append(TestQuestion(
                id=q['id'],
                content=q['content'],
                option_a="完全不同意",
                option_b="比较不同意",
                option_c="一般",
                option_d="比较同意",
                option_e="完全同意",
                category=q['category']
            ))
        return questions 