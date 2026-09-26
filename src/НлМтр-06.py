while True:
    n = int(input("Введите размерность n: "))

    if n > 0:
        print("Введите элементы квадратной матрицы:")

        above_main = 0
        below_main = 0
        above_side = 0
        below_side = 0
        matrix = []

        for i in range(n):
            matrix.append([])
            for j in range(n):
                num = float(input(f"Элемент [{i}][{j}]: "))
                matrix[i].append(num)

                if matrix[i][j] == 0:

                    if i < j:
                        above_main += 1
                    elif i > j:
                        below_main += 1

                    if i + j < n - 1:
                        above_side += 1
                    elif i + j > n - 1:
                        below_side += 1
        print(f"Кол-во нулей выше главной диагонали: {above_main}\nКол-во нулей ниже главной диагонали: {below_main}")
        print(f"Кол-во нулей выше побочной диагонали: {above_side}\nКол-во нулей ниже побочной диагонали: {below_side}")
    else:
        print("Ошибка. n <= 0. Повторите попытку.")

    nextt = input("Продолжить работу? (да/нет): ").strip()
    if nextt.lower() == "нет":
        print("Выход из программы.")
        break
    else:
        print("Новая матрица \n")
        