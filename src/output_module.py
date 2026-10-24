import json  # Импорт модуля для работы с транспортным протоколом JSON

def run():   # Функция вывода рез-в: загрузка данных из JSON-файла и отображение на экране
    # Протокол обмена: читаем результаты расчетов с обработкой ошибок взаимодействия
    try:
        # Открываем файл results.json в реж. чтения текста
        with open("results.json", "r", encoding="utf-8") as f:
            results = json.load(f)   # Считываем и восстанавливаем словарь с рез-ми из JSON-формата
    except (FileNotFoundError, json.JSONDecodeError, IOError):
        print("[Ошибка взаимодействия] Файл результатов results.json поврежден или отсутствует.")
        return False   # Возвращаем false, если файл не удалось прочитать
        
    # Вывод полученных данных в понятном пользователю виде в соответствии с полями JSON
    print("\n[Модуль вывода] Результаты анализа матрицы из JSON:")
    print(f"Кол-во нулей выше главной диагонали: {results['aboveMainZerosCount']}")
    print(f"Кол-во нулей ниже главной диагонали: {results['belowMainZerosCount']}")
    print(f"Кол-во нулей выше побочной диагонали: {results['aboveSideZerosCount']}")
    print(f"Кол-во нулей ниже побочной диагонали: {results['belowSideZerosCount']}\n")
    return True   # Успешное завершение работы ф-и
