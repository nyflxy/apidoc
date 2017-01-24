_author="niyoufa"

from enum import Enum

class DocType(Enum):
    UNKONWN = (0, "未知")
    JUDGEMENT = (1, "判决书")
    INDICTMENT = (7,"起诉书")

class CaseCause(Enum):
    THEFT = (201, "盗窃罪")
    INJURY_CRIME = (164, "故意伤害罪")