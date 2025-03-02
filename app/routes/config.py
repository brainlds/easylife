import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # 项目根目录
DATA_DIR = os.path.join(BASE_DIR, "data")
SCRIPT_DIR = os.path.join(DATA_DIR, "script")
SCRIPT_DIR_QUESTION_BANK = os.path.join(BASE_DIR, "question_bank")
