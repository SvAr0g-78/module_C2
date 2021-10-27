

from random import randint

class Dot:

    def __init__(self, x, y):   # Конструктор точки, по оси Х и У
        self.x = x      # Координаты точки по оси Х
        self.y = y          # Координаты точки по оси У

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):     # Метод отвечает как будет выводится класс в консоль
        return f"({self.x}, {self.y})"  # Возваращает точку при использовании print


class BoardException(Exception):
    pass

class BoardOutException(BoardException):
    def __str__(self):
        return "Вы пытаетесь выстрелить за границы доски!!!"


class BoardUsedException(BoardException):
    def __str__(self):
        return "Вы уже стреляли в это место!"


class BoardWrongShipException(BoardException):
    pass

class Ship:         # Класс Корабль
    def __init__(self, bow, l, o):  # Конструктор корабля
        self.bow = bow      # Координаты носа корабля
        self.l = l      # длина корабля
        self.o = o      # ориентир, вертикально - 1/горизонтально - 0
        self.lives = l

    @property
    def dots(self):     # метод выдает точки каробля
        ship_dots = []      # список точек корабля

        for i in range(self.l):     # перебераем каждую точку длины корабля
            cur_x = self.bow.x      # присваиваем нос по оси х
            cur_y = self.bow.y      # присваиваем нос по оси у

            if self.o == 0:     # если положение горизонтально =0
                cur_x += i      # шагаем по горизонтали на i точек
            elif self.o == 1:   # если положение вертикально =1
                cur_y += i      # шагаем по вертикали на i точек

            ship_dots.append(Dot(cur_x, cur_y))     # добавляем в список точки корабля
        return ship_dots    # возвращаем список с точками корабля

    def shooten(self, shot):    # метод проверяет попали в корабль
        return shot in self.dots


class Board:
    def __init__(self, hid=False, size=6):
        self.hid = hid      # покзывать доску или нет
        self.size = size    # размер поля
        self.count = 0      # сколько кораблей уничтоженно
        self.field = [["O"]*size for _ in range(size)]  # создаем доску и заполняем пусте О
        self.busy = []      # точки которые уже заняты
        self.ships = []     # список точек кораблей

    def add_ship(self, ship):  # добавлени корабля
        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = "■"  # добавляем на поле в координаты корабля квадрат
            self.busy.append(d)  # добаляем в список занятых координаты корабля
        self.ships.append(ship)
        self.contour(ship)

    def contour(self, ship, verb=False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not(self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "."
                self.busy.append(cur)

    def __str__(self):
        res = ""
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 | "

        for i, row in enumerate(self.field):  # перебераем строки поля вместе с индексом
            res += f"\n{i+1} | " + " | ".join(row) + " |"

        if self.hid:
            res = res.replace("■", "O")
        return res

    def out(self, d):  # выходит ли точка за пределы поля
        return not((0 <= d.x < self.size ) and (0 <= d.y < self.size))

    def shot(self, d):
        if self.out(d):
            raise BoardOutException()

        if d in self.busy:
            raise BoardUsedException()

        self.busy.append(d)

        for ship in self.ships:
            if d in ship.dots:
                ship.lives -= 1
                self.field[d.x][d.y] = "X"
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb = True)
                    print("Корабль уничтожен!!!")
                    return False
                else:
                    print("Корабль ранен!")
                    return True

        self.field[d.x][d.y] = "*"
        print("Мимо!")
        return False

    def begin(self):
        self.busy = []


class Game:
    def __init__(self, size = 6):
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hid = True

        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def random_board(self):
        board = None
        while board is None:
            board = self.random_place()
        return board

    def random_place(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)
        attempts = 0
        for l in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def greet(self):
        print('--------------------')
        print('  Приветствуем Вас  ')
        print('       в игре       ')
        print('     морской бой    ')
        print('--------------------')
        print('  формат ввода: x y ')
        print(' x - номер строки   ')
        print(' y - номер столбца  ')

    def loop(self):
        num = 0
        while True:
            print('-' * 20)
            print('Доска пользователя: ')
            print(self.us.board)
            print('-' * 20)
            print('Доска компьютера: ')
            print(self.ai.board)

            if num % 2 == 0:
                print('-' * 20)
                print('Ходит пользователь!')
                repeat = self.us.move()
            else:
                print('-' * 20)
                print('Ходит компьютер!')
                repeat = self.ai.move()

            if repeat:
                num -= 1

            if self.ai.board.count == 7:
                print('-' * 20)
                print('Пользователь выиграл!')
                break

            if self.us.board.count == 7:
                print('-' * 20)
                print('Компьютер выиграл!')
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()


class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)


class AI(Player):
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(f'Ход компьютера: {d.x+1} {d.y+1}')
        return d


class User(Player):
    def ask(self):
        while True:
            cords = input('Ваш ход: ').split()
            if len(cords) != 2:
                print('Введите 2 координаты!')
                continue

            x, y = cords
            if not (x.isdigit()) or not (y.isdigit()):
                print('Вы ввели не числа! Введите числа!')
                continue

            x, y = int(x), int(y)

            return  Dot(x-1, y-1)


g = Game()
g.start()



