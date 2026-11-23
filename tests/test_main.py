import output_module
import process_module
import input_module
import os
import sys
import json

# Подключаем папку /src, чтобы pytest видел тестируемые модули и корректно их импортировал
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))


# Unit-тестирование полного цикла работы программы

def test_integration_full_json_cycle(monkeypatch, tmp_path, capsys):
    """Интеграционный тест: сквозная передача данных input -> process -> output через JSON."""
    # Переключение текущей раб. директории во временную папку pytest, чтобы новые файлы не засоряли проект
    monkeypatch.chdir(tmp_path)

    # Имитация ввода единичной матрицы 2x2: [[1, 0], [0, 1]]
    inputs = iter(["2", "1", "0", "0", "1"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    # 1. Запуск модуля ввода — проверка успешного выполнениия, создание файла matrix.json
    assert input_module.run() is True
    assert (tmp_path / "matrix.json").exists()

    # 2. Запуск модуля обработки — чтение matrix.json, подсчёт нулей и сохранение results.json
    assert process_module.run() is True
    assert (tmp_path / "results.json").exists()

    # 3. Запуск модуля вывода — чтение results.json, запись итогов в консоль
    assert output_module.run() is True

    # Перехват консольного вывода, проверка корректности итоговых знач. для матрицы 2x2
    output = capsys.readouterr().out
    assert "Кол-во нулей выше главной диагонали: 1" in output
    assert "Кол-во нулей ниже главной диагонали: 1" in output
    # Для 2x2 побочная диагональ: (0,1),(1,0); выше (0,0)=1 -> 0 нулей, ниже (1,1)=1 -> 0 нулей
    assert "Кол-во нулей выше побочной диагонали: 0" in output
    assert "Кол-во нулей ниже побочной диагонали: 0" in output

    # Читаем рез-ты из файла и сверяем структуру
    # Проверка взаимодействия между process_module и output_module на ур-не данных
    with open(tmp_path / "results.json", "r", encoding="utf-8") as f:
        results = json.load(f)
    assert results == {
        "aboveMainZerosCount": 1,
        "belowMainZerosCount": 1,
        "aboveSideZerosCount": 0,
        "belowSideZerosCount": 0,
    }
