import fasttext
import json


def train_emotion_model():
    # Параметры обучения
    settings = {
        "input": r"D:/Software/Necessary/Dippploom/KOOOOD/MentalHealthApp/data/emotions.txt",
        "epoch": 50, # Количество проходов по данным
        "lr": 0.1,  # Скорость обучения
        "wordNgrams": 2, # Учитываем сочетания слов
        "dim": 100,
        "loss": "softmax"
    }

    # Дообучение модели
    model = fasttext.train_supervised(**settings)

    # Сохранение модели
    model.save_model(r"D:/Software/Necessary/Dippploom/KOOOOD/MentalHealthApp/model/emotion_model.bin")
    print("Модель успешно дообучена и сохранена")

if __name__ == "__main__":
    train_emotion_model()

# Загружаем предобученную модель
#model = fasttext.load_model(r'D:\Software\Necessary\Dippploom\KOOOOD\MentalHealthApp\data\cc.ru.300.bin')
