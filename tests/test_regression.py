import output_module
import process_module
import input_module
import os
import sys
import json

import pytest

# Добавляем директорию ../src в системные пути поиска модулей,
# чтобы pytest мог корректно импортировать тестируемые файлы проекта
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))


# Регрессионное тестирование: проверка ранее исправленных багов


@pytest.mark.regression  # Маркер для выборочного запуска регресс. тестов (pytest -m regression)
def test_regression_json_contract_keys(tmp_path, monkeypatch):
    """Регрессия BUG-01: проверка неизменности ключей протокола JSON v2.0."""
    # Изоляция файловых операций во временной директории pytest
    monkeypatch.chdir(tmp_path)

    # Имитация ввода матрицы 2x2: [[0, 1], [1, 0]]
    inputs = iter(["2", "0", "1", "1", "0"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    # Проверяем модули, они должны по цепочке успешно читать и записывать json-файлы,
    # не падая с KeyError из-за несовпадения имён полей в контракте данных
    assert input_module.run() is True
    assert process_module.run() is True
    assert output_module.run() is True

    # Явно сверяем имена полей — суть регрессии BUG-01
    with open(tmp_path / "results.json", encoding="utf-8") as f:
        results = json.load(f)
    assert set(results.keys()) == {
        "aboveMainZerosCount",
        "belowMainZerosCount",
        "aboveSideZerosCount",
        "belowSideZerosCount",
    }


@pytest.mark.regression
def test_regression_negative_and_float_elements(tmp_path, monkeypatch, capsys):
    """Регрессия базовой логики: корректная обработка отрицательных нулей (-0.0) и дробных чисел."""
    monkeypatch.chdir(tmp_path)

    # Имитация ввод аматрицы 3x3 с граничными веществ. значениями, включая '-0.0' и '0.0':
    # [[-0.0, 0.0,  0.0],
    #  [ 1.1, 2.2,  0.0],
    #  [ 0.0, 0.0,  3.3]]
    inputs = iter(["3", "-0.0", "0.0", "0.0", "1.1", "2.2", "0.0", "0.0", "0.0", "3.3"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    # Прогоняем цикл обработки и вывода
    assert input_module.run() is True
    assert process_module.run() is True
    assert output_module.run() is True

    # Перехват консольного вывода и проверка корректности распознавания '-0.0' как ноль
    out = capsys.readouterr().out
    assert "Кол-во нулей выше главной диагонали: 3" in out
    assert "Кол-во нулей ниже главной диагонали: 2" in out
    assert "Кол-во нулей выше побочной диагонали: 2" in out
    assert "Кол-во нулей ниже побочной диагонали: 2" in out
