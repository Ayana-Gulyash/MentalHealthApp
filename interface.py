import tkinter as tk
from tkinter import ttk, scrolledtext
from collections import defaultdict, Counter
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
from tkcalendar import DateEntry


class JournalEntryForm(tk.Frame):
    def __init__(self, parent, on_submit):
        super().__init__(parent)
        self.on_submit = on_submit
        self.configure(bg='#e0f7fa')

        self.style = ttk.Style()
        self.style.configure('TFrame', background='#e0f7fa')
        self.style.configure('TLabel', background='#e0f7fa', font=('Arial', 10))
        self.style.configure('TButton', font=('Arial', 10), background='#4db6ac')
        self.style.map('TButton', background=[('active', '#26a69a'), ('pressed', '#00897b')])

        self._create_widgets()
        self._layout_widgets()

        self.status_var = tk.StringVar()
        self.status_label = ttk.Label(self, textvariable=self.status_var, foreground='green')
        self.status_label.grid(row=11, column=0, columnspan=2)

        self.analysis_frame = ttk.Frame(self, style='TFrame')
        self.analysis_text = scrolledtext.ScrolledText(
            self.analysis_frame,
            wrap=tk.WORD,
            width=60,
            height=8,
            font=('Arial', 10),
            relief=tk.SOLID,
            borderwidth=1,
            bg='#ffffff'
        )
        self.analysis_text.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)
        self.analysis_frame.grid(row=12, column=0, columnspan=2, padx=10, pady=10, sticky='ew')

    def _create_widgets(self):
        self.lbl_title = ttk.Label(self, text="Дневник эмоций", font=('Arial', 14, 'bold'), foreground='#00796b')

        self.txt_description = scrolledtext.ScrolledText(
            self,
            width=60,
            height=5,
            font=('Arial', 10),
            relief=tk.SOLID,
            borderwidth=1,
            bg='#ffffff'
        )
        self.ent_triggers = tk.Entry(self, width=60, font=('Arial', 10), relief=tk.SOLID, borderwidth=1)
        self.ent_physical = tk.Entry(self, width=60, font=('Arial', 10), relief=tk.SOLID, borderwidth=1)
        self.ent_thoughts = tk.Entry(self, width=60, font=('Arial', 10), relief=tk.SOLID, borderwidth=1)

        self.lbl_description = ttk.Label(self, text="Описание ситуации:")
        self.lbl_triggers = ttk.Label(self, text="Триггеры (через запятую):")
        self.lbl_physical = ttk.Label(self, text="Физические ощущения (через запятую):")
        self.lbl_thoughts = ttk.Label(self, text="Автоматические мысли (через запятую):")

        self.btn_submit = ttk.Button(self, text="Проанализировать", command=self._submit)

    def _layout_widgets(self):
        self.lbl_title.grid(row=0, column=0, columnspan=2, pady=(10, 15))
        self.lbl_description.grid(row=1, column=0, sticky='w', padx=10)
        self.txt_description.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky='ew')

        self.lbl_triggers.grid(row=3, column=0, sticky='w', padx=10)
        self.ent_triggers.grid(row=4, column=0, columnspan=2, padx=10, pady=5, sticky='ew')

        self.lbl_physical.grid(row=5, column=0, sticky='w', padx=10)
        self.ent_physical.grid(row=6, column=0, columnspan=2, padx=10, pady=5, sticky='ew')

        self.lbl_thoughts.grid(row=7, column=0, sticky='w', padx=10)
        self.ent_thoughts.grid(row=8, column=0, columnspan=2, padx=10, pady=5, sticky='ew')

        self.btn_submit.grid(row=9, column=0, columnspan=2, pady=(15, 10))

    def _submit(self):
        text = self.txt_description.get("1.0", tk.END).strip()
        if not text:
            tk.messagebox.showwarning("Ошибка", "Введите описание ситуации!")
            return

        entry_data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "text": text,
            "triggers": [t.strip() for t in self.ent_triggers.get().split(",") if t.strip()],
            "physical_sensations": [p.strip() for p in self.ent_physical.get().split(",") if p.strip()],
            "thoughts": [th.strip() for th in self.ent_thoughts.get().split(",") if th.strip()]
        }

        self.on_submit(entry_data)

    def show_analysis(self, analysis):
        self.analysis_text.config(state='normal')
        self.analysis_text.delete(1.0, tk.END)

        if not analysis:
            self.analysis_text.insert(tk.END, "Не удалось выполнить анализ", 'error')
            return

        intensity = getattr(analysis, 'intensity', 0)
        probability = min(100, intensity * 10)

        self.analysis_text.insert(tk.END, "Результат анализа:\n\n", 'header')
        self.analysis_text.insert(tk.END, f"Выявленная эмоция: {analysis.manifested_emotion} ({probability}%)\n\n", 'result')

        self.analysis_text.insert(tk.END, "Рекомендации:\n", 'subheader')
        for rec in analysis.recommendation.get('short_term', []):
            self.analysis_text.insert(tk.END, f"- {rec}\n")

        about = analysis.recommendation.get('about', {})
        if about:
            self.analysis_text.insert(tk.END, "\nОБ ЭТОЙ ЭМОЦИИ:\n", 'subheader')
            self.analysis_text.insert(tk.END, f"{about.get('description', '')}\n")
            causes = about.get('causes', [])
            if causes:
                self.analysis_text.insert(tk.END, "\nВозможные причины:\n", 'subheader')
                for cause in causes:
                    self.analysis_text.insert(tk.END, f"- {cause}\n")

        self.analysis_text.config(state='disabled')

        self.analysis_text.tag_config('header', foreground='#00796b', font=('Arial', 10, 'bold'))
        self.analysis_text.tag_config('subheader', foreground='#00897b', font=('Arial', 9, 'bold'))
        self.analysis_text.tag_config('result', foreground='#00695c')
        self.analysis_text.tag_config('error', foreground='#c62828')

class DiaryView(tk.Frame):
    def __init__(self, parent, entries):
        super().__init__(parent)
        self.entries = entries
        self.configure(bg='#e0f7fa')

        self._prepare_filter_data()
        self.style = ttk.Style()
        self._setup_styles()
        self._create_widgets()
        self._layout_widgets()
        self._load_entries()
        self._setup_charts()

        self.tree.tag_configure('new', background='#e0f7fa')  # Новая запись — бирюзовый

        # Цвета по эмоциям
        self.tree.tag_configure('грусть', foreground='#1e88e5')  # Синий
        self.tree.tag_configure('тревога', foreground='#e53935')  # Красный
        self.tree.tag_configure('злость', foreground='#8e24aa')  # Фиолетовый
        self.tree.tag_configure('вина/стыд', foreground='#f4511e')  # Оранжевый
        self.tree.tag_configure('радость', foreground='#43a047')  # Зелёный
        self.tree.tag_configure('апатия/пустота', foreground='#757575')  # Серый
        self.tree.tag_configure('беспомощность/усталость', foreground='#5e35b1')  # Тёмно-фиолетовый

    def _get_entry_tags(self, entry):
        tags = []

        # Новые записи (меньше 5 минут назад)
        from datetime import datetime
        try:
            entry_time = datetime.strptime(entry.get('timestamp', ''), '%Y-%m-%d %H:%M')
            if (datetime.now() - entry_time).total_seconds() < 300:
                tags.append('new')
        except Exception:
            pass

        # Добавляем тег с названием эмоции
        emotion = entry.get('emotion', '').lower()
        if emotion:
            tags.append(emotion)

        return tags

    def update_entries(self, new_entries):
        """Обновляет таблицу и графики дневника новыми записями."""
        self.entries = new_entries

        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Сортировка и добавление записей
        sorted_entries = sorted(self.entries, key=lambda x: x.get('timestamp', ''), reverse=True)
        for entry in sorted_entries:
            timestamp = entry.get('timestamp', '')
            emotion = entry.get('emotion', '')
            triggers = ', '.join(entry.get('triggers', []))
            preview = ' '.join(entry.get('text', '').split()[:5]) + '...' if entry.get('text') else ''

            item_id = self.tree.insert('', 'end',
                                       values=(timestamp, emotion, triggers, preview),
                                       tags=self._get_entry_tags(entry))
            setattr(self.tree, f'entry_{item_id}', entry)

        # Обновляем графики, если они есть
        if hasattr(self, 'emotion_chart'):
            self.emotion_chart.update_chart(self.entries)
        if hasattr(self, 'trigger_chart'):
            self.trigger_chart.update_chart(self.entries)
        if hasattr(self, 'sensation_chart'):
            self.sensation_chart.update_chart(self.entries)

    def _prepare_filter_data(self):
        self.all_triggers = sorted(set(t for e in self.entries for t in e.get('triggers', [])))
        self.all_sensations = sorted(set(s for e in self.entries for s in e.get('physical_sensations', [])))
        self.all_thoughts = sorted(set(t for e in self.entries for t in e.get('thoughts', [])))

    def _setup_styles(self):
        self.style.configure('Diary.TFrame', background='#e0f7fa')
        self.style.configure('Diary.Treeview', font=('Arial', 9), rowheight=25, background='#ffffff', fieldbackground='#ffffff')
        self.style.configure('Diary.Treeview.Heading', font=('Arial', 10, 'bold'), background='#4db6ac', foreground='white')
        self.style.map('Diary.Treeview', background=[('selected', '#80deea')])

    def _create_widgets(self):
        self.filter_container = ttk.Frame(self)
        self.filter_canvas = tk.Canvas(self.filter_container, bg='#e0f7fa')
        scrollbar = ttk.Scrollbar(self.filter_container, orient='vertical', command=self.filter_canvas.yview)
        scrollbar.pack(side='right', fill='y')
        self.filter_canvas.configure(yscrollcommand=scrollbar.set)
        self.filter_canvas.pack(side='left', fill='both', expand=True)
        self.filter_frame = ttk.Frame(self.filter_canvas)
        self.filter_canvas.create_window((0, 0), window=self.filter_frame, anchor='nw')

        ttk.Label(self.filter_frame, text="Фильтры", font=('Arial', 11, 'bold')).grid(row=0, column=0, pady=5, sticky='w')
        ttk.Label(self.filter_frame, text="Эмоция:").grid(row=1, column=0, sticky='w')
        self.emotion_filter = ttk.Combobox(self.filter_frame, values=self._get_unique_emotions())
        self.emotion_filter.grid(row=1, column=1, sticky='ew', padx=5, pady=2)
        ttk.Label(self.filter_frame, text="Дата с:").grid(row=2, column=0, sticky='w')
        self.date_from = DateEntry(self.filter_frame, width=12, background='darkblue',
                                   foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.date_from.grid(row=2, column=1, sticky='ew', padx=5, pady=2)
        ttk.Label(self.filter_frame, text="Дата по:").grid(row=3, column=0, sticky='w')
        self.date_to = DateEntry(self.filter_frame, width=12, background='darkblue',
                                 foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.date_to.grid(row=3, column=1, sticky='ew', padx=5, pady=2)
        ttk.Label(self.filter_frame, text="Поиск по тексту:").grid(row=4, column=0, sticky='w')
        self.search_entry = ttk.Entry(self.filter_frame)
        self.search_entry.grid(row=4, column=1, sticky='ew', padx=5, pady=2)
        ttk.Label(self.filter_frame, text="Искать в:").grid(row=5, column=0, sticky='w')
        self.search_in = ttk.Combobox(self.filter_frame, values=["Событиях", "Мыслях", "Всем тексте"])
        self.search_in.set("Всем тексте")
        self.search_in.grid(row=5, column=1, sticky='ew', padx=5, pady=2)

        self.apply_btn = ttk.Button(self.filter_frame, text="Применить", command=self._apply_filters)
        self.apply_btn.grid(row=6, column=0, columnspan=2, pady=5)
        self.reset_btn = ttk.Button(self.filter_frame, text="Сбросить", command=self._reset_filters)
        self.reset_btn.grid(row=7, column=0, columnspan=2, pady=5)

        self.tree = ttk.Treeview(self, columns=('date', 'emotion', 'triggers', 'preview'), show='headings', selectmode='browse')
        self.tree.heading('date', text='Дата')
        self.tree.heading('emotion', text='Эмоция')
        self.tree.heading('triggers', text='Триггеры')
        self.tree.heading('preview', text='Событие')

        self.detail_frame = ttk.Frame(self)
        self.detail_text = scrolledtext.ScrolledText(self.detail_frame, wrap=tk.WORD, width=60, height=10, font=('Arial', 9))
        self.detail_text.config(state='disabled')
        self.detail_text.pack(fill='both', expand=True)

        self.tree.bind("<<TreeviewSelect>>", self._show_entry_details)

    def _layout_widgets(self):
        self.filter_container.grid(row=0, column=0, sticky='ns', padx=10, pady=10)
        self.tree.grid(row=0, column=1, sticky='nsew', padx=10, pady=10)
        self.detail_frame.grid(row=1, column=0, columnspan=2, sticky='nsew', padx=10, pady=10)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=1)

    def _setup_charts(self):
        self.notebook = ttk.Notebook(self.detail_frame)
        self.notebook.pack(fill='both', expand=True)

        chart_frame1 = ttk.Frame(self.notebook)
        self.notebook.add(chart_frame1, text="Эмоции по дням")
        self._plot_emotion_chart(chart_frame1)

        chart_frame2 = ttk.Frame(self.notebook)
        self.notebook.add(chart_frame2, text="Триггеры")
        self._plot_trigger_chart(chart_frame2)

        chart_frame3 = ttk.Frame(self.notebook)
        self.notebook.add(chart_frame3, text="Частые мысли")
        self._plot_thought_chart(chart_frame3)

        chart_frame4 = ttk.Frame(self.notebook)
        self.notebook.add(chart_frame4, text="Интенсивность эмоций")
        self._plot_intensity_chart(chart_frame4)

    def _plot_emotion_chart(self, parent):
        from collections import defaultdict
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

        emotion_by_day = defaultdict(lambda: defaultdict(int))

        for entry in self.entries:
            try:
                date = entry.get('timestamp', '')[:10]
                emotion = entry.get('emotion', '')
                if date and emotion:
                    emotion_by_day[date][emotion] += 1
            except:
                continue

        if not emotion_by_day:
            return

        sorted_dates = sorted(emotion_by_day.keys())
        emotions = sorted(set(e for daily in emotion_by_day.values() for e in daily))

        emotion_counts = {emotion: [] for emotion in emotions}
        for date in sorted_dates:
            for emotion in emotions:
                emotion_counts[emotion].append(emotion_by_day[date].get(emotion, 0))

        fig, ax = plt.subplots(figsize=(8, 4))
        for emotion, counts in emotion_counts.items():
            ax.plot(sorted_dates, counts, marker='o', label=emotion)

        ax.set_title("Динамика эмоций")
        ax.set_xlabel("Дата")
        ax.set_ylabel("Количество")
        ax.grid(True)
        ax.legend()

        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)

    def _plot_trigger_chart(self, parent):
        from collections import Counter
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

        all_triggers = [t for e in self.entries for t in e.get('triggers', [])]
        counter = Counter(all_triggers)
        top_triggers = counter.most_common(10)

        if not top_triggers:
            return

        labels = [t[0] for t in top_triggers]
        counts = [t[1] for t in top_triggers]

        fig, ax = plt.subplots(figsize=(8, 4))
        ax.barh(labels, counts, color='#4db6ac')
        ax.set_title("Частые триггеры")
        ax.set_xlabel("Частота")
        ax.set_ylabel("Триггеры")
        ax.invert_yaxis()

        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)

    def _plot_thought_chart(self, parent):
        from collections import Counter
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

        all_thoughts = [t for e in self.entries for t in e.get('thoughts', [])]
        counter = Counter(all_thoughts)
        top_thoughts = counter.most_common(10)

        if not top_thoughts:
            return

        labels = [t[0] for t in top_thoughts]
        counts = [t[1] for t in top_thoughts]

        fig, ax = plt.subplots(figsize=(8, 4))
        ax.barh(labels, counts, color='#ff8a65')
        ax.set_title("Частые мысли")
        ax.set_xlabel("Частота")
        ax.set_ylabel("Мысли")
        ax.invert_yaxis()

        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)

    def _plot_intensity_chart(self, parent):
        from collections import defaultdict
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

        # Собираем интенсивности по эмоциям и дням
        intensity_by_day = defaultdict(lambda: defaultdict(list))

        for entry in self.entries:
            date = entry.get('timestamp', '')[:10]
            emotion = entry.get('emotion', '')
            intensity = entry.get('intensity', 0)
            if emotion and intensity > 0:
                intensity_by_day[emotion][date].append(intensity)

        if not intensity_by_day:
            return

        fig, ax = plt.subplots(figsize=(8, 4))

        for emotion, dates in intensity_by_day.items():
            sorted_dates = sorted(dates)
            avg_values = [sum(dates[d]) / len(dates[d]) for d in sorted_dates]
            ax.plot(sorted_dates, avg_values, marker='o', label=emotion)

            # Добавим подписи к точкам
            for i, val in enumerate(avg_values):
                ax.annotate(f"{val:.1f}", (sorted_dates[i], val), textcoords="offset points", xytext=(0, 5),
                            ha='center')

        ax.set_title("Интенсивность эмоций по дням")
        ax.set_xlabel("Дата")
        ax.set_ylabel("Средняя интенсивность (0–10)")
        ax.set_ylim(0, 10)
        ax.grid(True)
        ax.legend()

        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)

    def _get_unique_emotions(self):
        return list(set(
            e.get('emotion', '') for e in self.entries
            if e.get('emotion')
        ))

    def _apply_filters(self):
        filtered = self.entries.copy()

        # Фильтр по эмоции
        emotion = self.emotion_filter.get()
        if emotion:
            filtered = [e for e in filtered if e.get('emotion') == emotion]

        # Фильтр по датам
        try:
            if self.date_from.get():
                date_f = datetime.strptime(self.date_from.get(), '%Y-%m-%d').date()
                filtered = [e for e in filtered if datetime.strptime(e['timestamp'], '%Y-%m-%d %H:%M').date() >= date_f]

            if self.date_to.get():
                date_t = datetime.strptime(self.date_to.get(), '%Y-%m-%d').date()
                filtered = [e for e in filtered if datetime.strptime(e['timestamp'], '%Y-%m-%d %H:%M').date() <= date_t]
        except ValueError:
            pass

        # Фильтр по тексту
        search_text = self.search_entry.get().lower()
        if search_text:
            search_in = self.search_in.get()
            filtered = [e for e in filtered if self._matches_search(e, search_text, search_in)]

        self._update_display(filtered)

    def _matches_search(self, entry, text, search_in):
        """Проверяет совпадение текста в записи"""
        if search_in == "Событиях":
            return text in entry.get('text', '').lower()
        elif search_in == "Мыслях":
            return any(text in thought.lower() for thought in entry.get('thoughts', []))
        else:  # Весь текст
            return (
                    text in entry.get('text', '').lower() or
                    any(text in thought.lower() for thought in entry.get('thoughts', []))
            )

    def _reset_filters(self):
        """Сбрасывает все фильтры"""
        self.emotion_filter.set('')
        self.date_from.delete(0, tk.END)
        self.date_to.delete(0, tk.END)
        self.search_entry.delete(0, tk.END)
        self.search_in.set("Всем тексте")
        self._apply_filters()

    def _show_entry_details(self, event=None):
        """Показывает подробности выбранной записи"""
        selected = self.tree.focus()
        if not selected:
            return

        values = self.tree.item(selected, 'values')
        timestamp = values[0]

        # Ищем запись по времени
        entry = next((e for e in self.entries if e.get('timestamp') == timestamp), None)
        if not entry:
            return

        self.detail_text.config(state='normal')
        self.detail_text.delete(1.0, tk.END)

        details = f"""Дата: {entry.get('timestamp', '')}
    Эмоция: {entry.get('emotion', '')}
    Интенсивность: {entry.get('intensity', '')}/10
    -----------------------------
    Событие:
    {entry.get('text', '')}

    Триггеры: {', '.join(entry.get('triggers', []))}
    Физические ощущения: {', '.join(entry.get('physical_sensations', []))}
    Мысли: {', '.join(entry.get('thoughts', []))}
    """

        if 'recommendation' in entry:
            details += "\nРекомендации:\n"
            for rec in entry['recommendation'].get('short_term', []):
                details += f"- {rec}\n"

        self.detail_text.insert(tk.END, details)
        self.detail_text.config(state='disabled')

    def _load_entries(self):
        """Загружает записи в таблицу"""
        self.tree.delete(*self.tree.get_children())

        sorted_entries = sorted(self.entries, key=lambda e: e.get('timestamp', ''), reverse=True)

        for entry in sorted_entries:
            timestamp = entry.get('timestamp', '')
            emotion = entry.get('emotion', '')
            triggers = ', '.join(entry.get('triggers', []))
            preview = ' '.join(entry.get('text', '').split()[:5]) + '...' if entry.get('text') else ''

            self.tree.insert('', 'end', values=(timestamp, emotion, triggers, preview))

    def _update_display(self, entries):
        """Обновляет отображение таблицы и графиков"""
        self.tree.delete(*self.tree.get_children())

        for entry in sorted(entries, key=lambda e: e.get('timestamp', ''), reverse=True):
            timestamp = entry.get('timestamp', '')
            emotion = entry.get('emotion', '')
            triggers = ', '.join(entry.get('triggers', []))
            preview = ' '.join(entry.get('text', '').split()[:5]) + '...' if entry.get('text') else ''

            self.tree.insert('', 'end', values=(timestamp, emotion, triggers, preview))

        # Обновим графики
        self._update_charts(entries)

    def _update_charts(self, entries):
        """Обновляет графики на основе отфильтрованных данных"""
        for tab in self.notebook.tabs():
            self.notebook.forget(tab)

        chart_frame1 = ttk.Frame(self.notebook)
        self.notebook.add(chart_frame1, text="Эмоции по дням")
        self._plot_emotion_chart(chart_frame1)

        chart_frame2 = ttk.Frame(self.notebook)
        self.notebook.add(chart_frame2, text="Триггеры")
        self._plot_trigger_chart(chart_frame2)

        chart_frame3 = ttk.Frame(self.notebook)
        self.notebook.add(chart_frame3, text="Частые мысли")
        self._plot_thought_chart(chart_frame3)

        chart_frame4 = ttk.Frame(self.notebook)
        self.notebook.add(chart_frame4, text="Интенсивность эмоций")
        self._plot_intensity_chart(chart_frame4)
