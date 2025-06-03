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


"""
# Связующая таблица для эмоциональных паттернов и рекомендаций
pattern_recommendations = db.Table('pattern_recommendations', db.metadata,
    db.Column('emotional_pattern_id', db.Integer, db.ForeignKey('emotional_state_patterns.id'), primary_key=True),
    db.Column('recommendation_id', db.Integer, db.ForeignKey('recommendations.id'), primary_key=True)
)

# Связующая таблица для негативных паттернов и рекомендаций
negative_pattern_recommendations = db.Table('negative_pattern_recommendations', db.metadata,
    db.Column('negative_pattern_id', db.Integer, db.ForeignKey('negative_patterns.id'), primary_key=True),
    db.Column('recommendation_id', db.Integer, db.ForeignKey('recommendations.id'), primary_key=True)
)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(120), unique=True)
    registration_date = db.Column(db.DateTime, default=db.func.now())

    # Связи с другими таблицами
    journal_entries = db.relationship('JournalEntry', backref='user', lazy=True)
    user_analysis_history = db.relationship('UserAnalysisHistory', backref='user', lazy=True)
    help_message_templates = db.relationship('HelpMessageTemplate', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'

class JournalEntry(db.Model):
    __tablename__ = 'journal_entries'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=db.func.now())
    situation_text = db.Column(db.Text, nullable=False)
    primary_emotion = db.Column(db.String(50), nullable=False)
    emotion_intensity = db.Column(db.Integer, nullable=False)
    emotion_probability = db.Column(db.Float)  # Вероятность эмоции (опционально)
    thoughts_text = db.Column(db.Text)  # Общее поле для мыслей (если нет отдельной таблицы)
    physical_sensations_text = db.Column(db.Text)  # Общее поле для ощущений (если нет отдельной таблицы)
    triggers_text = db.Column(db.Text)  # Общее поле для триггеров (если нет отдельной таблицы)
    recommendations_json = db.Column(db.Text) # Для хранения рекомендаций в формате JSON (временное решение)

    # Связи с другими таблицами (если вы решите использовать отдельные таблицы)
    triggers = db.relationship('Trigger', backref='journal_entry', lazy=True)
    physical_sensations = db.relationship('PhysicalSensation', backref='journal_entry', lazy=True)
    automatic_thoughts = db.relationship('AutomaticThought', backref='journal_entry', lazy=True)

    def __repr__(self):
        return f'<JournalEntry {self.timestamp} by User {self.user_id}>'

class Trigger(db.Model):
    __tablename__ = 'triggers'
    id = db.Column(db.Integer, primary_key=True)
    entry_id = db.Column(db.Integer, db.ForeignKey('journal_entries.id'), nullable=False)
    trigger_text = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f'<Trigger "{self.trigger_text}" for Entry {self.entry_id}>'

class PhysicalSensation(db.Model):
    __tablename__ = 'physical_sensations'
    id = db.Column(db.Integer, primary_key=True)
    entry_id = db.Column(db.Integer, db.ForeignKey('journal_entries.id'), nullable=False)
    sensation_text = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f'<PhysicalSensation "{self.sensation_text}" for Entry {self.entry_id}>'

class AutomaticThought(db.Model):
    __tablename__ = 'automatic_thoughts'
    id = db.Column(db.Integer, primary_key=True)
    entry_id = db.Column(db.Integer, db.ForeignKey('journal_entries.id'), nullable=False)
    thought_text = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'<AutomaticThought "{self.thought_text}" for Entry {self.entry_id}>'

class Recommendation(db.Model):
    __tablename__ = 'recommendations'
    id = db.Column(db.Integer, primary_key=True)
    emotion = db.Column(db.String(50), nullable=False)
    short_advice = db.Column(db.Text)
    description = db.Column(db.Text)
    scientific_sources = db.Column(db.Text)
    recommendation_type = db.Column(db.String(50), nullable=False)

    # Связи с другими таблицами
    emotional_patterns = db.relationship('EmotionalStatePattern', secondary=pattern_recommendations, backref='recommendations')
    negative_patterns = db.relationship('NegativePattern', secondary=negative_pattern_recommendations, backref='recommendations')
    user_analysis_history = db.relationship('UserAnalysisHistory', backref='recommendation', lazy=True)

    def __repr__(self):
        return f'<Recommendation for {self.emotion} ({self.recommendation_type})>'

class EmotionalStatePattern(db.Model):
    __tablename__ = 'emotional_state_patterns'
    id = db.Column(db.Integer, primary_key=True)
    pattern_name = db.Column(db.String(100), nullable=False)
    pattern_description = db.Column(db.Text)

    # Связь с таблицей рекомендаций (определена в Recommendation)

    def __repr__(self):
        return f'<EmotionalStatePattern "{self.pattern_name}">'

class NegativePattern(db.Model):
    __tablename__ = 'negative_patterns'
    id = db.Column(db.Integer, primary_key=True)
    pattern_description = db.Column(db.Text)

    # Связь с таблицей рекомендаций (определена в Recommendation)

    def __repr__(self):
        return f'<NegativePattern "{self.pattern_description[:50]}...">'

class UserAnalysisHistory(db.Model):
    __tablename__ = 'user_analysis_history'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    analysis_timestamp = db.Column(db.DateTime, nullable=False, default=db.func.now())
    emotional_pattern_id = db.Column(db.Integer, db.ForeignKey('emotional_state_patterns.id'))
    negative_pattern_id = db.Column(db.Integer, db.ForeignKey('negative_patterns.id'))
    recommendation_id = db.Column(db.Integer, db.ForeignKey('recommendations.id'))
    analysis_details = db.Column(db.Text)

    # Связи с другими таблицами
    user = db.relationship('User', backref='analysis_history')
    emotional_pattern = db.relationship('EmotionalStatePattern', backref='user_analysis_history')
    negative_pattern = db.relationship('NegativePattern', backref='user_analysis_history')
    recommendation = db.relationship('Recommendation', backref='user_analysis_history')

    def __repr__(self):
        return f'<UserAnalysis at {self.analysis_timestamp} for User {self.user_id}>'


class HelpMessageTemplate(db.Model):
    __tablename__ = 'help_message_templates'
    id = db.Column(db.Integer, primary_key=True)
    template_name = db.Column(db.String(100), nullable=False)
    message_text = db.Column(db.Text, nullable=False)
    is_default = db.Column(db.Boolean, default=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    user = db.relationship('User', backref='help_message_templates')

    def __repr__(self):
        return f'<HelpTemplate "{self.template_name}">'
"""