import os
import json
import sys

# Добавляем папку src в пути поиска модулей, для того, чтобы тесты её видели
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

import process_module


def test_process_module_json_flow():
    # Создаем искусственную тестовую матрицу 3х3
    test_matrix = [[1.0, 0.0, 3.0], [0.0, 5.0, 0.0], [7.0, 8.0, 0.0]]

    # Записываем её в JSON, имитируя работу нового модуля ввода
    with open("matrix.json", "w", encoding="utf-8") as f:
        json.dump(test_matrix, f)

    # Запускаем ваш модуль обработки
    status = process_module.run()

    # Проверяем, что модуль отработал успешно (вернул True)
    assert status is True

    # Проверяем, что создался файл результатов в формате JSON
    assert os.path.exists("results.json")

    # Читаем результаты расчетов
    with open("results.json", "r", encoding="utf-8") as f:
        results = json.load(f)

    # Проверяем, правильно ли подсчетались нули и соотв. маппингу camelCase
    assert results["aboveMainZerosCount"] == 2  # 2 нуля выше главной диагонали
    assert results["belowMainZerosCount"] == 1  # 1 нуль ниже главной диагонали

    # Очищаем временные файлы после проведения теста
    if os.path.exists("matrix.json"):
        os.remove("matrix.json")
    if os.path.exists("results.json"):
        os.remove("results.json")

