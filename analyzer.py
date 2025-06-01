# 2. analyzer.py - Логика анализа
import fasttext
from collections import Counter, defaultdict
from data_models import JournalEntry, ImmediateAnalysis, LongTermAnalysis
import json
from datetime import datetime

class EmotionAnalyzer:
    def __init__(self):
        self.entries = []
        self.model = None

        # Проверка существования методов
        if not hasattr(self, '_generate_recommendations'):
            print("⚠️ ВНИМАНИЕ: Метод _generate_recommendations не найден!")

        try:
            # ЗАГРУЖАЕМ FastText-МОДЕЛЬ
            self.model = fasttext.load_model("model/emotion_model.bin")
        except Exception as e:
            print(f"[ОШИБКА] Не удалось загрузить модель: {str(e)}")
            print("Убедитесь, что файл model/emotion_model.bin существует")

    def analyze_entry(self, entry_data):
        """Анализирует новую запись и возвращает ImmediateAnalysis"""
        try:
            entry = JournalEntry(**entry_data)
        except Exception as e:
            print(f"Ошибка создания записи: {e}")
            return None

        if not self.model:
            entry.emotion = "неизвестно"
            entry.intensity = 0
            return ImmediateAnalysis(
                manifested_emotion=entry.emotion,
                intensity=entry.intensity,
                recommendation=self._generate_recommendations(entry)
            )

        try:
            labels, probs = self.model.predict(entry.text)
            entry.emotion = labels[0].replace("__label__", "")
            entry.intensity = int(probs[0] * 10)
        except Exception as e:
            print(f"Ошибка предсказания эмоции: {e}")
            return None

            # 🔽 Убедись, что здесь `entry` уже есть!
        analysis = ImmediateAnalysis(
            manifested_emotion=entry.emotion,
            intensity=entry.intensity,
            recommendation=self._generate_recommendations(entry)
        )

        self.entries.append(entry)
        return analysis

    def generate_long_term_report(self):
        if not self.entries:
            return None

        total_entries = len(self.entries)

        # Динамика эмоций по дням
        emotion_by_date = defaultdict(lambda: defaultdict(int))
        for entry in self.entries:
            date = entry.timestamp.split(' ')[0]
            emotion = entry.emotion
            intensity = entry.intensity
            emotion_by_date[date][emotion] += intensity

        # Преобразуем defaultdict в обычный dict
        emotion_trend = {d: dict(em) for d, em in emotion_by_date.items()}

        # Анализ эмоций
        emotion_counts = Counter(e.emotion for e in self.entries if hasattr(e, 'emotion'))
        most_common_emotion, count = emotion_counts.most_common(1)[0]
        emotion_percent = int(count / total_entries * 100)

        # Анализ триггеров
        all_triggers = [t for e in self.entries for t in getattr(e, 'triggers', [])]
        trending_triggers = [t[0] for t in Counter(all_triggers).most_common(3)] if all_triggers else ["Нет данных"]

        # Физические симптомы
        all_sensations = [s for e in self.entries for s in getattr(e, 'physical_sensations', [])]
        common_sensations = [s[0] for s in Counter(all_sensations).most_common(2)] if all_sensations else ["Нет данных"]

        # Мысли
        all_thoughts = [t for e in self.entries for t in getattr(e, 'thoughts', [])]
        # Осознанные (частые) мысли
        common_thoughts = [t[0] for t in Counter(all_thoughts).most_common(5)]

        # Факторы риска (исправленный вызов)
        risk_factors = self._identify_risk_factors(all_thoughts)

        return LongTermAnalysis(
            most_common_emotion=f"{most_common_emotion} ({emotion_percent}% записей)",
            trending_triggers=trending_triggers,
            physiological_pattern=f"Чаще всего: {', '.join(common_sensations)}",
            cognitive_pattern=f"Частые мысли: {', '.join(f'«{t}»' for t in common_thoughts)}",
            psychological_state=self._assess_mental_state(),
            risk_factors=risk_factors,
            recommendation=self._long_term_recommendations(most_common_emotion),
            emotion_trend=emotion_trend,  # 👈 Новое
            risky_thoughts=common_thoughts  # 👈 Новое
        )

    def _generate_recommendations(self, entry):
        # Загружаем рекомендации из JSON
        print(f"▶ _generate_recommendations вызван. Entry: {entry}")
        default_rec = {
            "short_term": ["Рекомендации не найдены"],
            "scientific_references": [],
            "about": {
                "description": "Описание недоступно",
                "causes": []
            }
        }

        try:
            with open("data/recommendations.json", encoding="utf-8") as f:
                raw = f.read().lstrip('\ufeff')  # удаляем BOM
                recommendations = json.loads(raw)
            result = recommendations.get(entry.emotion.lower(), default_rec)
            print("✔ Рекомендации найдены:", result)
            return result
        except Exception as e:
            print("Ошибка загрузки рекомендаций:", e)
            return default_rec

    def _get_common_items(self, field):
        all_items = [item for entry in self.entries for item in getattr(entry, field)]
        if not all_items:  # Если список пуст
            return ["Нет данных"]
        return [item[0] for item in Counter(all_items).most_common(3)]

    def _get_pattern(self, field):
        items = self._get_common_items(field)
        return f"Чаще всего: {', '.join(items)}"

    def _assess_mental_state(self, emotion_counts=None, total_entries=None):
        """Оценивает психологическое состояние на основе записей"""
        if not hasattr(self, 'entries') or not self.entries:
            return "Недостаточно данных для оценки"

        # Если аргументы не переданы, вычисляем их
        if emotion_counts is None or total_entries is None:
            emotion_counts = Counter(e.emotion for e in self.entries if hasattr(e, 'emotion'))
            total_entries = len(self.entries)

        # Упрощенная логика оценки
        emotions = [e.emotion for e in self.entries if hasattr(e, 'emotion')]

        if emotions.count('страх') / len(emotions) > 0.5:
            return "Возможное тревожное расстройство"
        elif emotions.count('грусть') / len(emotions) > 0.5:
            return "Возможное депрессивное состояние"
        elif emotions.count('гнев') / len(emotions) > 0.4:
            return "Повышенная раздражительность"
        else:
            return "Нормальное состояние"

    def _identify_risk_factors(self, thoughts=None):
        """Более надежная версия с проверкой ввода и возвратом словаря"""
        if thoughts is None:
            if not hasattr(self, 'entries'):
                return {"": "Недостаточно данных"}
            thoughts = [t for e in self.entries for t in getattr(e, 'thoughts', [])]

        if not thoughts:
            return {"": "Не выявлены"}

        results = {}

        negative_patterns = {
            'перфекционизм': ['должен быть идеальным', 'не могу ошибаться'],
            'социальная тревожность': ['меня осудят', 'будут смеяться'],
            'катастрофизация': ['все будет плохо', 'это катастрофа'],
            'самокритика': ['я неудачник', 'я ничего не стою'],
            'беспомощность': ['я не справлюсь', 'это бесполезно']
        }

        for factor, patterns in negative_patterns.items():
            if any(any(pattern in thought.lower() for pattern in patterns) for thought in thoughts):
                results[factor] = f"Выражены мысли, связанные с паттерном '{factor}'."

        if not results:
            return {"": "Не выявлены"}

        return results

    def _long_term_recommendations(self, emotion: str):
        return {
            "long_term": [
                "Регулярная практика медитации",
                "Ведение дневника настроения"
            ],
            "professional_help": {
                "when_to_consider": "Если симптомы сохраняются более 2 недель",
                "recommended_professionals": ["клинический психолог", "психотерапевт"],
                "resources": [
                    "https://www.psychiatry.org",
                    "https://pubmed.ncbi.nlm.nih.gov"
                ]
            }
        }