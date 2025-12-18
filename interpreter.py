import sys
import struct
import csv
from enum import Enum
from typing import List, Dict, Any


class Opcode(Enum):
    """Коды операций УВМ"""
    LOAD_CONST = 1      # Загрузка константы (A=1)
    ADD = 3             # Сложение (A=3)
    STORE = 4           # Запись в память (A=4)
    LOAD_MEM = 7        # Чтение из памяти (A=7)


class UVMInterpreter:
    def __init__(self, memory_size=65536):
        self.memory = [0] * memory_size  # Память данных
        self.code_memory = []           # Память команд
        self.stack = []                 # Стек УВМ
        self.pc = 0                     # Счетчик команд
        self.running = False
        self.memory_size = memory_size
        
    def load_binary(self, binary_path: str):
        """Загрузка бинарной программы"""
        with open(binary_path, 'rb') as f:
            data = f.read()
        
        # Загружаем команды по 3 байта
        self.code_memory.clear()
        for i in range(0, len(data), 3):
            chunk = data[i:i+3]
            if len(chunk) == 3:
                self.code_memory.append(chunk)
            elif len(chunk) > 0:
                # Дополняем нулями если нужно
                chunk = chunk + bytes([0] * (3 - len(chunk)))
                self.code_memory.append(chunk)
        
        print(f"Загружено {len(self.code_memory)} команд")
    
    def decode_instruction(self, instr_bytes: bytes) -> Dict[str, Any]:
        """Декодирование бинарной команды"""
        if len(instr_bytes) != 3:
            raise ValueError(f"Неверная длина команды: {len(instr_bytes)} байт")
        
        # Объединяем 3 байта в 24-битное слово (little-endian)
        word = (instr_bytes[2] << 16) | (instr_bytes[1] << 8) | instr_bytes[0]
        
        # Извлекаем поле A (биты 0-2)
        a_field = word & 0x07
        
        # Извлекаем поле B (биты 3-19)
        b_field = (word >> 3) & 0xFFFF
        
        try:
            opcode = Opcode(a_field)
        except ValueError:
            raise ValueError(f"Неизвестный код операции: {a_field}")
        
        return {
            'opcode': opcode,
            'b_field': b_field,
            'raw': instr_bytes
        }
    
    def execute_load_const(self, b_field: int):
        """Выполнение загрузки константы"""
        self.stack.append(b_field)
        print(f"LOAD_CONST: загружена константа {b_field}, стек: {self.stack}")
    
    def execute_store(self, b_field: int):
        """Выполнение записи в память"""
        if not self.stack:
            raise RuntimeError("Стек пуст при выполнении STORE")
        
        value = self.stack.pop()
        if 0 <= b_field < self.memory_size:
            self.memory[b_field] = value
            print(f"STORE: записано значение {value} по адресу {b_field}")
        else:
            raise RuntimeError(f"Недопустимый адрес памяти: {b_field}")
    
    def execute_load_mem(self):
        """Выполнение чтения из памяти"""
        if not self.stack:
            raise RuntimeError("Стек пуст при выполнении LOAD_MEM")
        
        address = self.stack.pop()
        if 0 <= address < self.memory_size:
            value = self.memory[address]
            self.stack.append(value)
            print(f"LOAD_MEM: прочитано значение {value} из адреса {address}, стек: {self.stack}")
        else:
            raise RuntimeError(f"Недопустимый адрес памяти: {address}")
    
    def execute_add(self):
        """Выполнение сложения"""
        if len(self.stack) < 2:
            raise RuntimeError("Недостаточно операндов в стеке для ADD")
        
        # Второй операнд снимается первым
        op2 = self.stack.pop()
        # Первый операнд - из памяти по адресу из стека
        address = self.stack.pop()
        
        if 0 <= address < self.memory_size:
            op1 = self.memory[address]
            result = op1 + op2
            self.stack.append(result)
            print(f"ADD: {op1} + {op2} = {result} (адрес: {address}), стек: {self.stack}")
        else:
            raise RuntimeError(f"Недопустимый адрес памяти: {address}")
    
    def run(self):
        """Основной цикл выполнения"""
        self.running = True
        self.pc = 0
        
        print("=== Начало выполнения программы ===")
        
        while self.running and self.pc < len(self.code_memory):
            instr_bytes = self.code_memory[self.pc]
            
            try:
                instr = self.decode_instruction(instr_bytes)
            except ValueError as e:
                print(f"Ошибка декодирования команды: {e}")
                break
            
            print(f"[PC={self.pc:04d}] {instr['opcode'].name} B={instr['b_field']}")
            
            try:
                if instr['opcode'] == Opcode.LOAD_CONST:
                    self.execute_load_const(instr['b_field'])
                elif instr['opcode'] == Opcode.STORE:
                    self.execute_store(instr['b_field'])
                elif instr['opcode'] == Opcode.LOAD_MEM:
                    self.execute_load_mem()
                elif instr['opcode'] == Opcode.ADD:
                    self.execute_add()
                else:
                    print(f"Неизвестная команда: {instr['opcode']}")
                    break
                    
            except RuntimeError as e:
                print(f"Ошибка выполнения: {e}")
                break
            
            self.pc += 1
        
        self.running = False
        print(f"\nВыполнение завершено. PC={self.pc}")
        print(f"Состояние стека: {self.stack}")
    
    def save_memory_dump(self, output_path: str, start_addr: int, end_addr: int):
        """Сохранение дампа памяти в CSV"""
        if start_addr < 0 or end_addr > self.memory_size or start_addr >= end_addr:
            raise ValueError(f"Некорректный диапазон адресов: {start_addr}-{end_addr}")
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Адрес', 'Значение', 'Шестнадцатеричное'])
            
            for addr in range(start_addr, end_addr):
                value = self.memory[addr]
                writer.writerow([addr, value, f"0x{value:04X}"])
        
        print(f"Дамп памяти сохранен в {output_path} ({end_addr-start_addr} записей)")


def test_array_copy():
    """Тестовая программа: копирование массива"""
    print("\n=== Тест: Копирование массива ===")
    
    # Создаем простую программу для копирования массива
    program = """
        ; Копирование 5 элементов из адресов 100-104 в 200-204
        
        ; Загружаем счетчик
        LOAD #5
        STORE 99    ; Сохраняем счетчик в памяти
        
    loop:
        ; Проверяем счетчик
        LOAD 99
        LOAD #0
        ; Здесь должна быть команда сравнения, но её нет
        ; Упростим: будем выполнять фиксированное число итераций
        
        ; Вычисляем исходный адрес
        LOAD #100
        LOAD 99
        ; Не хватает вычитания, упрощаем
        
        ; Просто копируем каждый элемент отдельно
    """
    
    # Вместо этого создадим прямую программу
    direct_program = """
        ; Копируем элемент 0
        LOAD 100
        STORE 200
        
        ; Копируем элемент 1
        LOAD 101
        STORE 201
        
        ; Копируем элемент 2
        LOAD 102
        STORE 202
        
        ; Копируем элемент 3
        LOAD 103
        STORE 203
        
        ; Копируем элемент 4
        LOAD 104
        STORE 204
    """
    
    return direct_program


def test_addition():
    """Тестовая программа: сложение"""
    print("\n=== Тест: Сложение чисел ===")
    
    program = """
        ; Сложение двух чисел: memory[300] + memory[301] = memory[302]
        
        ; Загружаем первое число
        LOAD #300
        LOAD
        
        ; Загружаем второе число
        LOAD #301
        LOAD
        
        ; Складываем
        ADD
        
        ; Сохраняем результат
        STORE 302
    """
    
    return program


def test_vector_addition():
    """Тестовая программа: сложение вектора с константой"""
    print("\n=== Тест: Сложение вектора с константой ===")
    
    program = """
        ; Вектор из 7 элементов (100-106) складываем с 157
        ; Результат записываем в 200-206
        
        ; Элемент 0
        LOAD 100
        LOAD #157
        ADD
        STORE 200
        
        ; Элемент 1
        LOAD 101
        LOAD #157
        ADD
        STORE 201
        
        ; Элемент 2
        LOAD 102
        LOAD #157
        ADD
        STORE 202
        
        ; Элемент 3
        LOAD 103
        LOAD #157
        ADD
        STORE 203
        
        ; Элемент 4
        LOAD 104
        LOAD #157
        ADD
        STORE 204
        
        ; Элемент 5
        LOAD 105
        LOAD #157
        ADD
        STORE 205
        
        ; Элемент 6
        LOAD 106
        LOAD #157
        ADD
        STORE 206
    """
    
    return program


def main():
    """Основная функция CLI"""
    
    if len(sys.argv) < 5:
        print("Использование:")
        print("  python interpreter.py <бинарный_файл> <выходной_csv> <начальный_адрес> <конечный_адрес>")
        print()
        print("Примеры тестов:")
        print("  python interpreter.py --test-copy")
        print("  python interpreter.py --test-add")
        print("  python interpreter.py --test-vector")
        return
    
    if sys.argv[1] == "--test-copy":
        # Тест копирования массива
        from assembler import Assembler
        
        # Создаем тестовые данные
        interpreter = UVMInterpreter()
        for i in range(5):
            interpreter.memory[100 + i] = i * 10  # 0, 10, 20, 30, 40
        
        # Создаем и компилируем программу
        program = test_array_copy()
        assembler = Assembler()
        binary = assembler.assemble_to_binary(program, test_mode=False)
        
        # Сохраняем во временный файл
        with open("temp_copy.bin", "wb") as f:
            f.write(binary)
        
        # Загружаем и выполняем
        interpreter.load_binary("temp_copy.bin")
        interpreter.run()
        
        # Выводим результаты
        print("\nРезультаты копирования:")
        for i in range(5):
            src = interpreter.memory[100 + i]
            dst = interpreter.memory[200 + i]
            print(f"  memory[{100+i}] = {src} -> memory[{200+i}] = {dst}")
        
        interpreter.save_memory_dump("copy_dump.csv", 95, 210)
        return
    
    elif sys.argv[1] == "--test-add":
        # Тест сложения
        from assembler import Assembler
        
        interpreter = UVMInterpreter()
        interpreter.memory[300] = 42
        interpreter.memory[301] = 58
        
        program = test_addition()
        assembler = Assembler()
        binary = assembler.assemble_to_binary(program, test_mode=False)
        
        with open("temp_add.bin", "wb") as f:
            f.write(binary)
        
        interpreter.load_binary("temp_add.bin")
        interpreter.run()
        
        print(f"\nРезультат сложения: {interpreter.memory[300]} + {interpreter.memory[301]} = {interpreter.memory[302]}")
        interpreter.save_memory_dump("add_dump.csv", 295, 310)
        return
    
    elif sys.argv[1] == "--test-vector":
        # Тест сложения вектора
        from assembler import Assembler
        
        interpreter = UVMInterpreter()
        # Заполняем исходный вектор
        for i in range(7):
            interpreter.memory[100 + i] = i * 20
        
        program = test_vector_addition()
        assembler = Assembler()
        binary = assembler.assemble_to_binary(program, test_mode=False)
        
        with open("temp_vector.bin", "wb") as f:
            f.write(binary)
        
        interpreter.load_binary("temp_vector.bin")
        interpreter.run()
        
        print("\nРезультаты сложения вектора:")
        for i in range(7):
            src = interpreter.memory[100 + i]
            res = interpreter.memory[200 + i]
            print(f"  {src} + 157 = {res}")
        
        interpreter.save_memory_dump("vector_dump.csv", 95, 210)
        return
    
    # Обычный режим работы
    binary_file = sys.argv[1]
    output_csv = sys.argv[2]
    start_addr = int(sys.argv[3])
    end_addr = int(sys.argv[4])
    
    interpreter = UVMInterpreter()
    
    try:
        interpreter.load_binary(binary_file)
        interpreter.run()
        interpreter.save_memory_dump(output_csv, start_addr, end_addr)
    except FileNotFoundError:
        print(f"Ошибка: файл '{binary_file}' не найден")
    except Exception as e:
        print(f"Ошибка выполнения: {e}")


if __name__ == "__main__":
    main()
