from tkinter import scrolledtext
from datetime import datetime
import json
import os
import tkinter as tk
from tkinter import ttk, messagebox
from interface import JournalEntryForm, DiaryView
from analyzer import EmotionAnalyzer
from data_models import LongTermAnalysis, JournalEntry
from collections import defaultdict

class MentalHealthApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Монитор психического состояния")
        self.root.geometry("1000x800")
        self.root.configure(bg='#e0f7fa')

        self.entries = []  # Инициализация списка записей
        self.analyzer = EmotionAnalyzer()

        self._setup_styles()
        self._setup_ui()
        self._load_initial_data()
        self._setup_diary_tab()
        self._setup_summary_tab()

        self._setup_education_tab()

        self.status_var = tk.StringVar()
        self.status_label = ttk.Label(self.root, textvariable=self.status_var, foreground='green', font=('Arial', 10))
        self.status_label.pack(side='bottom', pady=5)

    def _setup_education_tab(self):
        self.tab_edu = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_edu, text="Обо мне")

        left_frame = ttk.Frame(self.tab_edu)
        right_frame = ttk.Frame(self.tab_edu)
        left_frame.pack(side='left', fill='y', padx=10, pady=10)
        right_frame.pack(side='right', fill='both', expand=True, padx=10, pady=10)

        self.emo_listbox = tk.Listbox(left_frame, font=('Arial', 11))
        self.emo_listbox.pack(fill='y')

        self.edu_text = scrolledtext.ScrolledText(right_frame, wrap=tk.WORD, font=('Arial', 10))
        self.edu_text.pack(fill='both', expand=True)

        # Загрузка информации
        try:
            with open(r'D:/Software/Necessary/Dippploom/KOOOOD/MentalHealthApp/data/emotions_info.json', 'r', encoding='utf-8') as f:
                self.emotion_info = json.load(f)
                for emotion in self.emotion_info.keys():
                    self.emo_listbox.insert(tk.END, emotion.capitalize())
        except Exception as e:
            self.emotion_info = {}
            self.edu_text.insert(tk.END, f"Ошибка загрузки данных: {str(e)}")

        # Обработчик выбора
        self.emo_listbox.bind('<<ListboxSelect>>', self._show_emo_info)

    def _show_emo_info(self, event):
        selected = self.emo_listbox.curselection()
        if not selected:
            return
        emotion = self.emo_listbox.get(selected[0]).lower()
        info = self.emotion_info.get(emotion, {})

        self.edu_text.config(state='normal')
        self.edu_text.delete(1.0, tk.END)

        self.edu_text.insert(tk.END, f"{emotion.capitalize()}\n\n", 'title')
        self.edu_text.insert(tk.END, f"Описание:\n{info.get('description', '')}\n\n")

        self.edu_text.insert(tk.END, "Возможные причины:\n")
        for cause in info.get('causes', []):
            self.edu_text.insert(tk.END, f"- {cause}\n")

        self.edu_text.insert(tk.END, "\nКак справляться:\n")
        for tip in info.get('how_to_deal', []):
            self.edu_text.insert(tk.END, f"- {tip}\n")

        self.edu_text.config(state='disabled')

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('.', background='#e0f7fa')
        style.configure('TNotebook', background='#b2ebf2', borderwidth=0)
        style.configure('TNotebook.Tab',
                        background='#80deea',
                        padding=[15, 5],
                        font=('Arial', 10))
        style.map('TNotebook.Tab',
                  background=[('selected', '#4db6ac')],
                  foreground=[('selected', 'white')])

    def _setup_ui(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Вкладка новой записи
        self.tab_new_entry = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_new_entry, text="Новая запись")

        self.entry_form = JournalEntryForm(
            self.tab_new_entry,
            self._process_journal_entry
        )
        self.entry_form.pack(fill='both', expand=True, padx=20, pady=20)

    def _load_initial_data(self):
        """Загружает начальные данные при запуске"""
        try:
            if os.path.exists(r'D:/Software/Necessary/Dippploom/KOOOOD/MentalHealthApp/data/journal_entries.json'):
                with open(r'D:/Software/Necessary/Dippploom/KOOOOD/MentalHealthApp/data/journal_entries.json', "r", encoding="utf-8") as f:
                    self.entries = json.load(f)

                # 👇 Загружаем записи в EmotionAnalyzer
                self.analyzer.entries = [
                    JournalEntry(**entry) for entry in self.entries if isinstance(entry, dict)
                ]
        except Exception as e:
            print(f"Ошибка загрузки: {e}")
            self.entries = []

    def _setup_diary_tab(self):
        """Создает вкладку дневника"""
        self.tab_diary = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_diary, text="Дневник")

        # Нормализация структуры записей
        normalized_entries = []
        for entry in self.entries:
            if isinstance(entry, dict):
                normalized = {
                    'timestamp': entry.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M')),
                    'text': entry.get('text', ''),
                    'triggers': entry.get('triggers', []),
                    'physical_sensations': entry.get('physical_sensations', []),
                    'thoughts': entry.get('thoughts', []),
                    'emotion': entry.get('emotion', '')
                }
                normalized_entries.append(normalized)

        self.diary_view = DiaryView(self.tab_diary, normalized_entries)
        self.diary_view.pack(fill='both', expand=True)

    def _save_entries(self):
        """Сохраняет записи в файл"""
        try:
            os.makedirs('data', exist_ok=True)
            with open('data/journal_entries.json', 'w', encoding='utf-8') as f:
                json.dump(self.entries, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить записи: {str(e)}")

    def _process_journal_entry(self, entry_data):
        """Обрабатывает новую запись без переключения вкладки"""
        try:
            analysis = self.analyzer.analyze_entry(entry_data)
            if analysis:
                # Показываем анализ в текущей вкладке
                self.entry_form.show_analysis(analysis)

                # Создаем полную запись
                new_entry = {
                    'timestamp': entry_data['timestamp'],
                    'text': entry_data['text'],
                    'triggers': entry_data['triggers'],
                    'physical_sensations': entry_data['physical_sensations'],
                    'thoughts': entry_data['thoughts'],
                    'emotion': analysis.manifested_emotion,
                    'intensity': getattr(analysis, 'intensity', 0),
                    'recommendation': analysis.recommendation
                }

                # Добавляем запись
                self.entries.insert(0, new_entry)

                # Сохраняем и обновляем дневник (без переключения вкладки)
                self._save_entries()
                self._update_diary()

                # Показываем уведомление о успешном добавлении
                messagebox.showinfo("Готово", "Запись успешно добавлена в дневник")
                # В _process_journal_entry после успешного добавления
                self.status_var.set("Запись добавлена в дневник")
                self.root.after(3000, lambda: self.status_var.set(""))

                self.status_var.set("Ты молодец, что следишь за собой 💚")
                self.root.after(3000, lambda: self.status_var.set(""))


        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось проанализировать запись: {str(e)}")

    def _update_diary(self):
        """Обновляет дневник в фоновом режиме"""
        if hasattr(self, 'diary_view') and self.diary_view.winfo_exists():
            try:
                # Обновляем только если вкладка видима
                if self.notebook.tab(self.tab_diary, 'state') == 'normal':
                    self.diary_view.update_entries(self.entries)
            except Exception as e:
                print(f"Фоновое обновление дневника: {e}")

    def _setup_summary_tab(self):
        """Создает вкладку с общим анализом"""
        self.tab_summary = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_summary, text="Общее состояние")

        # Создаем текстовое поле с прокруткой
        self.summary_text = scrolledtext.ScrolledText(
            self.tab_summary,
            wrap=tk.WORD,
            width=80,
            height=25,
            font=('Arial', 10),
            bg='white'
        )
        self.summary_text.pack(fill='both', expand=True, padx=10, pady=10)

        # Настройка тегов для форматирования
        self.summary_text.tag_configure('header', font=('Arial', 12, 'bold'))
        self.summary_text.tag_configure('important', foreground='#d32f2f')
        self.summary_text.tag_configure('recommendation', foreground='#00796b')

        # Первоначальное обновление данных
        self._update_summary()

    def _update_summary(self):
        """Генерирует и показывает сводный анализ"""
        if not hasattr(self, 'summary_text'):
            return

        # Генерируем анализ
        report = self.analyzer.generate_long_term_report()
        if not report:
            return

        # Форматируем вывод
        summary = f"""САМОЕ ВАЖНОЕ О ВАШЕМ СОСТОЯНИИ:

    1. Преобладающая эмоция: {report.most_common_emotion}
    2. Частые триггеры: {', '.join(report.trending_triggers)}
    3. Физические симптомы: {report.physiological_pattern}
    4. Паттерны мышления: {report.cognitive_pattern}
    5. Психологическое состояние: {report.psychological_state}
    """

        # 👁 Часто повторяющиеся (осознанные) мысли
        summary += "\nОСОЗНАННЫЕ МЫСЛИ (на что стоит обратить внимание):\n"
        if report.risky_thoughts:
            for thought in report.risky_thoughts:
                summary += f"- «{thought}»\n"
        else:
            summary += "Нет выраженных повторяющихся мыслей.\n"

        # ⚠️ Пояснения к рискам
        summary += "\nФАКТОРЫ РИСКА:\n"
        if isinstance(report.risk_factors, dict):
            for risk, explanation in report.risk_factors.items():
                if risk.strip():
                    summary += f"- {risk.capitalize()}: {explanation}\n"
                else:
                    summary += f"- {explanation}\n"
        elif isinstance(report.risk_factors, list):
            for risk in report.risk_factors:
                summary += f"- {risk}\n"

        # 📈 Динамика эмоций
        summary += "\nДИНАМИКА ЭМОЦИЙ ПО ДНЯМ:\n"
        for date, emotions in report.emotion_trend.items():
            line = f"{date}: " + ", ".join(f"{emotion} — {count}" for emotion, count in emotions.items())
            summary += line + "\n"

        # 💡 Рекомендации
        summary += "\nРЕКОМЕНДАЦИИ:\n"
        for rec in report.recommendation['long_term']:
            summary += f"- {rec}\n"

        summary += "\nКОГДА ОБРАТИТЬСЯ К СПЕЦИАЛИСТУ:\n"
        summary += f"{report.recommendation['professional_help']['when_to_consider']}\n\n"

        summary += "РЕСУРСЫ:\n"
        for resource in report.recommendation['professional_help']['resources']:
            summary += f"- {resource}\n"

        # Отображение в текстовом поле
        self.summary_text.config(state='normal')
        self.summary_text.delete(1.0, tk.END)
        self.summary_text.insert(tk.END, summary)
        self.summary_text.config(state='disabled')

    def _update_diary(self):
        if hasattr(self, 'diary_view'):
            self.diary_view.update_entries(self.entries)
        self._update_summary()  # Обновляем сводку


if __name__ == "__main__":
    root = tk.Tk()
    app = MentalHealthApp(root)
    root.mainloop()