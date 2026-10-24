import os
import pickle
import sys

# Добавляем папку src в пути поиска модулей, для того, чтобы тесты её видели
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

import process_module


def test_process_module_zeros_count():
    # Создаем искусственную тестовую матрицу 3х3
    test_matrix = [[1.0, 0.0, 3.0], [0.0, 5.0, 0.0], [7.0, 8.0, 0.0]]

    # Записываем её в бинарный файл, для имитации работы модуля ввода
    with open("matrix.bin", "wb") as f:
        pickle.dump(test_matrix, f)

    # Запускаем ваш модуль обработки
    status = process_module.run()

    # Проверяем, что модуль отработал успешно (вернул True)
    assert status is True

    # Проверяем, что создался файл с рез-ми
    assert os.path.exists("results.bin")

    # Читаем рез-ты расчетов
    with open("results.bin", "rb") as f:
        results = pickle.load(f)

    # Проверяем, верно ли подсчитаны нули для тестовой матрицы
    assert (
        results["above_main"] == 1
    )  # Нулей строго выше главной диагонали: 1 (элемент)
    assert (
        results["below_main"] == 1
    )  # Нулей строго ниже главной диагонали: 1 (элемент)

    # Очищаем временные файлы после проведения теста
    if os.path.exists("matrix.bin"):
        os.remove("matrix.bin")
    if os.path.exists("results.bin"):
        os.remove("results.bin")
