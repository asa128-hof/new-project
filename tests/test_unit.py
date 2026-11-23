import main
import output_module
import process_module
import input_module
import os
import sys
import json
import pytest

# Подключаем папку/src, чтобы pytest видел тестируемые модули и корректно их импортировал
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))


# 1. Unit-тестирование модуля input_module
def test_input_valid_matrix(monkeypatch, tmp_path):
    """Проверка корректности ввода матрицы 2x2 и записи данных в файл matrix.json."""
    # Переключение текущей раб. директории во временную папку pytest, чтобы новые файлы не засоряли проект
    monkeypatch.chdir(tmp_path)
    # n = '2', далее 4 элемента: 4, 0, 0, -1
    inputs = iter(["2", "4", "0", "0", "-1"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    # Проверка работоспособности ф-и, создание целевого JSON-файла
    assert input_module.run() is True
    assert (tmp_path / "matrix.json").exists()

    # Чтение созданного файла, сравнение сохранённой структуры М с ожидаемой
    with open(tmp_path / "matrix.json", "r", encoding="utf-8") as f:
        saved_matrix = json.load(f)
    assert saved_matrix == [[4, 0.0], [0.0, -1.0]]


# Запуск одного и того же теста с набором некорректных знач. n
@pytest.mark.parametrize("invalid_n", ["0", "-5", "abc", ""])
def test_input_invalid_dimension(monkeypatch, tmp_path, invalid_n):
    """Проверка реакции на граничные (некорректные) значения размерности матрицы n."""
    monkeypatch.chdir(tmp_path)
    # Подменяем input() таким образом, чтобы всегда возвращалось тек. невалидное знач.
    monkeypatch.setattr("builtins.input", lambda _: invalid_n)

    # Ожидание возврата False и отсутствие созданного файла
    assert input_module.run() is False
    assert not (tmp_path / "matrix.json").exists()


def test_input_invalid_element(monkeypatch, tmp_path):
    """Проверка обработки ошибки ввода нечислового значения вместо эл-та матрицы."""
    monkeypatch.chdir(tmp_path)
    # Задана корректная размерность '2', первый элемент '10'. Далее невалидная строка
    inputs = iter(["2", "10", "ошибка"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    # Ф-я должна перехватить ошибку преобразования типа и вернуть False
    assert input_module.run() is False
    # Файл не должен остаться на диске после неудачного ввода
    assert not (tmp_path / "matrix.json").exists()


def test_input_io_error(monkeypatch, tmp_path):
    """Проверка обработки ошибки ввода-вывода (IOError) при сохранении matrix.json."""
    monkeypatch.chdir(tmp_path)
    # Вводим корректную матрицу 1x1 со значением '5'
    inputs = iter(["1", "5"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    # Имитируем сбой файловой системы при попытке открыть файл на запись
    def mock_open(*args, **kwargs):
        raise IOError("Нет прав на запись")

    monkeypatch.setattr("builtins.open", mock_open)
    # Ожидаем корректный перехват исключения и возврат False
    assert input_module.run() is False


# 2. Unit-тестирование модуля обработки данных (process_module)
def test_process_file_not_found(monkeypatch, tmp_path):
    """Проверка возврата False при отсутствии входного файла matrix.json."""
    monkeypatch.chdir(tmp_path)
    # Если в пустой временной папке файла нет, то модуль должен вернуть False
    assert process_module.run() is False


def test_process_corrupted_json(monkeypatch, tmp_path):
    """Проверка корректной обработки синтаксически повреждённого JSON-файла."""
    monkeypatch.chdir(tmp_path)
    # Создание файла с невалидным содержимым
    (tmp_path / "matrix.json").write_text("{broken_json", encoding="utf-8")
    assert process_module.run() is False
    # results.json не должен появиться при ошибке
    assert not (tmp_path / "results.json").exists()


def test_process_zeros_all_diagonals(monkeypatch, tmp_path):
    """Проверка подсчёта нулей относительно гл. и побочн. диагоналей (М 3x3)."""
    monkeypatch.chdir(tmp_path)
    # Подготовка тест-матрицы с известными нулями
    matrix = [
        [0.0, 0.0, 1.0],
        [0.0, 5.0, 0.0],
        [2.0, 0.0, 0.0],
    ]
    with open(tmp_path / "matrix.json", "w", encoding="utf-8") as f:
        json.dump(matrix, f)

    # Запуск расчётов. Формирование файла results.json
    assert process_module.run() is True
    assert (tmp_path / "results.json").exists()

    # Результаты вычислений загружаем и проверяем счётчики
    with open(tmp_path / "results.json", "r", encoding="utf-8") as f:
        results = json.load(f)
    assert results == {
        "aboveMainZerosCount": 2,
        "belowMainZerosCount": 2,
        "aboveSideZerosCount": 3,
        "belowSideZerosCount": 3,
    }


def test_process_no_zeros(monkeypatch, tmp_path):
    """Проверка граничного случая: в матрице нет нулевых эл-в."""
    monkeypatch.chdir(tmp_path)
    matrix = [[1.0, 2.0], [3.0, 4.0]]
    with open(tmp_path / "matrix.json", "w", encoding="utf-8") as f:
        json.dump(matrix, f)

    assert process_module.run() is True
    with open(tmp_path / "results.json", "r", encoding="utf-8") as f:
        results = json.load(f)
    # Все счётчики нулей должны быть 0
    assert results == {
        "aboveMainZerosCount": 0,
        "belowMainZerosCount": 0,
        "aboveSideZerosCount": 0,
        "belowSideZerosCount": 0,
    }


@pytest.mark.parametrize("matrix, expected", [
    # 1x1: единственный 0 лежит и на главной, и на побочной — счётчики должны быть 0
    ([[0.0]], {
        "aboveMainZerosCount": 0, "belowMainZerosCount": 0,
        "aboveSideZerosCount": 0, "belowSideZerosCount": 0,
    }),
    # 2x2 со всеми нулями. Главная: (0,0),(1,1); побочная: (0,1),(1,0).
    # Выше главной: (0,1)=0 -> 1;  ниже главной: (1,0)=0 -> 1.
    # Выше побочной: (0,0)=0 -> 1; ниже побочной: (1,1)=0 -> 1.
    ([[0.0, 0.0], [0.0, 0.0]], {
        "aboveMainZerosCount": 1, "belowMainZerosCount": 1,
        "aboveSideZerosCount": 1, "belowSideZerosCount": 1,
    }),
])
def test_process_small_sizes(monkeypatch, tmp_path, matrix, expected):
    """Граничные размерности 1x1 и 2x2."""
    monkeypatch.chdir(tmp_path)
    with open(tmp_path / "matrix.json", "w", encoding="utf-8") as f:
        json.dump(matrix, f)

    assert process_module.run() is True
    with open(tmp_path / "results.json", "r", encoding="utf-8") as f:
        results = json.load(f)
    assert results == expected


# 3. Unit-тестирование модуля вывода (output_module)
def test_output_file_not_found(monkeypatch, tmp_path):
    """Проверка возврата False при отсутствии файла с рез-ми results.json."""
    monkeypatch.chdir(tmp_path)
    assert output_module.run() is False


def test_output_success_print(monkeypatch, tmp_path, capsys):
    """Проверка корректного форматирования и вывода результатов в консоль."""
    monkeypatch.chdir(tmp_path)
    # Формирование тест-файла results.json с заранее заданными знач-ми
    mock_results = {
        "aboveMainZerosCount": 1,
        "belowMainZerosCount": 2,
        "aboveSideZerosCount": 3,
        "belowSideZerosCount": 2,
    }
    with open(tmp_path / "results.json", "w", encoding="utf-8") as f:
        json.dump(mock_results, f)

    assert output_module.run() is True
    # Перехват выведенного текста в поток вывода (stdout)
    output = capsys.readouterr().out
    assert "Кол-во нулей выше главной диагонали: 1" in output
    assert "Кол-во нулей ниже главной диагонали: 2" in output
    assert "Кол-во нулей выше побочной диагонали: 3" in output
    assert "Кол-во нулей ниже побочной диагонали: 2" in output


def test_output_corrupted_json(monkeypatch, tmp_path):
    """Проверка возврата False при синтаксически повреждённом results.json."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / "results.json").write_text("{not_a_json", encoding="utf-8")
    assert output_module.run() is False


# 4. Unit-тестирование главного модуля (main)
def test_main_retry_and_exit(monkeypatch, tmp_path, capsys):
    """Проверка перезапуска цикла при ошибке ввода и штатного выхода при ответе 'нет'."""
    monkeypatch.chdir(tmp_path)
    # Отключаем time.sleep для мгновенного выполнения тестов
    monkeypatch.setattr("time.sleep", lambda _: None)
    # Сценарий ввода юзера:
    # 1ая итерация: Неверная размерность '0' -> Запрос на повторный ввод
    # 2ая итерация: матрица 1x1 со значе '0' -> "Продолжить работу?" 'нет' -> Выход из программы
    inputs = iter(["0", "1", "0", "нет"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    main.main()
    # Проверка на наличие ожидаемых служ. соо в консоли
    output = capsys.readouterr().out
    assert "Повторите попытку ввода." in output
    assert "Выход из программы. Работа завершена." in output


def test_main_keyboard_interrupt(monkeypatch, tmp_path, capsys):
    """Проверка корректной обработки прерывания программы пользователем (Ctrl+C)."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("time.sleep", lambda _: None)
    # Первые 2 вызова — n='1' и элемент='5'; на 3-м (запрос продолжения) — Ctrl+C
    inputs = iter(["1", "5"])
    calls = {"n": 0}

    def mock_input(prompt):
        calls["n"] += 1
        if calls["n"] > 2:
            raise KeyboardInterrupt
        return next(inputs)

    monkeypatch.setattr("builtins.input", mock_input)
    main.main()
    # Убеждаемся, что программа не упала с трейсбеком, а вывела корректное сообщение
    output = capsys.readouterr().out
    assert "Программа прервана пользователем" in output


def test_main_continue_yes_then_no(monkeypatch, tmp_path, capsys):
    """Две итерации: ответ 'да' -> повторный расчёт, затем 'нет' -> выход."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("time.sleep", lambda _: None)
    # Итерация 1: n=1, элемент=0, ответ='да'
    # Итерация 2: n=1, элемент=1, ответ='нет'
    inputs = iter(["1", "0", "да", "1", "1", "нет"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    main.main()
    output = capsys.readouterr().out
    assert "Выход из программы. Работа завершена." in output
# Оба расчёта должны пройти, results.json перезаписан вторым
    with open(tmp_path / "results.json", "r", encoding="utf-8") as f:
        results = json.load(f)
        assert results == {
            "aboveMainZerosCount": 0, "belowMainZerosCount": 0,
            "aboveSideZerosCount": 0, "belowSideZerosCount": 0,
        }
