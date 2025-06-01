import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import Counter
from datetime import datetime


class EmotionChart:
    def __init__(self, parent, entries):
        self.parent = parent
        self.entries = entries
        self._setup_ui()

    def _setup_ui(self):
        self.frame = ttk.Frame(self.parent)
        self.fig, self.ax = plt.subplots(figsize=(8, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)
        self.update_chart()

    def update_chart(self, filtered_entries=None):
        entries = filtered_entries if filtered_entries else self.entries
        emotions = [e.get('emotion', '') for e in entries if e.get('emotion')]

        self.ax.clear()
        if emotions:
            emotion_counts = Counter(emotions)
            self.ax.bar(emotion_counts.keys(), emotion_counts.values(), color='#4db6ac')
            self.ax.set_title('Распределение эмоций')
            self.ax.set_ylabel('Количество')
        self.canvas.draw()


class TriggerChart:
    def __init__(self, parent, entries):
        self.parent = parent
        self.entries = entries
        self._setup_ui()

    def _setup_ui(self):
        self.frame = ttk.Frame(self.parent)
        self.fig, self.ax = plt.subplots(figsize=(8, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)
        self.update_chart()

    def update_chart(self, filtered_entries=None):
        entries = filtered_entries if filtered_entries else self.entries
        triggers = []
        for entry in entries:
            triggers.extend(entry.get('triggers', []))

        self.ax.clear()
        if triggers:
            trigger_counts = Counter(triggers)
            top_triggers = trigger_counts.most_common(10)
            self.ax.barh([t[0] for t in top_triggers],
                         [t[1] for t in top_triggers],
                         color='#4db6ac')
            self.ax.set_title('Топ 10 триггеров')
            self.ax.set_xlabel('Количество')
        self.canvas.draw()


class SensationChart:
    def __init__(self, parent, entries):
        self.parent = parent
        self.entries = entries
        self._setup_ui()

    def _setup_ui(self):
        self.frame = ttk.Frame(self.parent)
        self.fig, self.ax = plt.subplots(figsize=(8, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)
        self.update_chart()

    def update_chart(self, filtered_entries=None):
        entries = filtered_entries if filtered_entries else self.entries
        sensations = []
        for entry in entries:
            sensations.extend(entry.get('physical_sensations', []))

        self.ax.clear()
        if sensations:
            sensation_counts = Counter(sensations)
            top_sensations = sensation_counts.most_common(10)
            self.ax.barh([t[0] for t in top_sensations],
                         [t[1] for t in top_sensations],
                         color='#4db6ac')
            self.ax.set_title('Топ 10 физических ощущений')
            self.ax.set_xlabel('Количество')
        self.canvas.draw()