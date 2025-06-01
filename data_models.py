from datetime import datetime
from typing import List, Dict, Optional, Union
from pydantic import BaseModel

# 📘 Запись в дневнике
class JournalEntry(BaseModel):
    timestamp: str
    text: str
    triggers: List[str]
    physical_sensations: List[str]
    thoughts: List[str]
    emotion: str = ""
    intensity: int = 0

# 📊 Немедленный анализ эмоции
class ImmediateAnalysis(BaseModel):
    manifested_emotion: str
    intensity: int
    recommendation: Dict[str, Union[List[str], Dict[str, Union[str, List[str]]]]]
    # Поддерживает:
    # - short_term: List[str]
    # - scientific_references: List[str]
    # - about: { description: str, causes: List[str] }

# 📈 Долгосрочный анализ
class LongTermAnalysis(BaseModel):
    most_common_emotion: str
    trending_triggers: List[str]
    physiological_pattern: str
    cognitive_pattern: str
    psychological_state: str
    risk_factors: Dict[str, str]  # уже добавлено ранее
    risky_thoughts: Optional[List[str]] = []  # ← ДОБАВЬ ЭТО
    recommendation: Dict
    emotion_trend: Dict[str, Dict[str, int]] = {}
