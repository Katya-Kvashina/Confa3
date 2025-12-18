from enum import Enum
from typing import List, Tuple

# Константы УВМ
MEMORY_SIZE = 65536        # Размер памяти данных (64K)
MAX_CONSTANT = 511         # Максимальное значение константы (9 бит)
MAX_ADDRESS = 0xFFFF       # Максимальный адрес (16 бит)
INSTRUCTION_SIZE = 3       # Размер команды в байтах


class Opcode(Enum):
    """Коды операций УВМ"""
    LOAD_CONST = 1      # Загрузка константы (A=1)
    ADD = 3             # Сложение (A=3)
    STORE = 4           # Запись в память (A=4)
    LOAD_MEM = 7        # Чтение из памяти (A=7)
    
    @staticmethod
    def from_mnemonic(mnemonic: str) -> 'Opcode':
        """Преобразование мнемоники в opcode"""
        mnemonic = mnemonic.upper()
        mapping = {
            "LOAD_CONST": Opcode.LOAD_CONST,
            "LOAD": Opcode.LOAD_MEM,  # Для чтения из памяти
            "STORE": Opcode.STORE,
            "ADD": Opcode.ADD
        }
        return mapping.get(mnemonic)


class Memory:
    """Модель памяти УВМ"""
    
    def __init__(self, size: int = MEMORY_SIZE):
        self.data = [0] * size
        self.size = size
    
    def read(self, address: int) -> int:
        """Чтение из памяти"""
        if 0 <= address < self.size:
            return self.data[address]
        else:
            raise ValueError(f"Адрес вне диапазона: {address}")
    
    def write(self, address: int, value: int):
        """Запись в память"""
        if 0 <= address < self.size:
            self.data[address] = value
        else:
            raise ValueError(f"Адрес вне диапазона: {address}")
    
    def dump_range(self, start: int, end: int) -> List[Tuple[int, int]]:
        """Дамп диапазона памяти"""
        result = []
        for addr in range(start, min(end, self.size)):
            result.append((addr, self.data[addr]))
        return result
    
    def clear(self):
        """Очистка памяти"""
        self.data = [0] * self.size


class Stack:
    """Стек УВМ"""
    
    def __init__(self, max_size: int = 1024):
        self.data = []
        self.max_size = max_size
    
    def push(self, value: int):
        """Добавление значения в стек"""
        if len(self.data) >= self.max_size:
            raise RuntimeError("Переполнение стека")
        self.data.append(value)
    
    def pop(self) -> int:
        """Извлечение значения из стека"""
        if not self.data:
            raise RuntimeError("Стек пуст")
        return self.data.pop()
    
    def peek(self) -> int:
        """Просмотр верхнего элемента стека без извлечения"""
        if not self.data:
            raise RuntimeError("Стек пуст")
        return self.data[-1]
    
    def is_empty(self) -> bool:
        """Проверка на пустоту"""
        return len(self.data) == 0
    
    def size(self) -> int:
        """Размер стека"""
        return len(self.data)
    
    def clear(self):
        """Очистка стека"""
        self.data.clear()


def validate_constant(value: int) -> bool:
    """Проверка, что константа в допустимом диапазоне"""
    return 0 <= value <= MAX_CONSTANT


def validate_address(address: int) -> bool:
    """Проверка, что адрес в допустимом диапазоне"""
    return 0 <= address <= MAX_ADDRESS


def format_instruction_bytes(bytes_data: bytes) -> str:
    """Форматирование байтов команды для вывода"""
    return ', '.join(f'0x{b:02X}' for b in bytes_data)


def parse_number(value_str: str) -> int:
    """Парсинг числа из строки (десятичное или шестнадцатеричное)"""
    value_str = value_str.strip().upper()
    
    if value_str.startswith('0X'):
        # Шестнадцатеричное число
        return int(value_str[2:], 16)
    elif value_str.startswith('#'):
        # Константа с решёткой
        num_str = value_str[1:]
        if num_str.startswith('0X'):
            return int(num_str[2:], 16)
        else:
            return int(num_str)
    else:
        # Десятичное число
        return int(value_str)


def create_test_data():
    """Создание тестовых данных для демонстрации"""
    
    # Тест 1: Простая программа
    test1 = {
        'name': 'Загрузка и сохранение константы',
        'code': 'LOAD #155\nSTORE 1000',
        'expected_memory': {1000: 155}
    }
    
    # Тест 2: Сложение
    test2 = {
        'name': 'Сложение двух чисел',
        'code': 'LOAD #300\nLOAD\nLOAD #301\nLOAD\nADD\nSTORE 302',
        'init_memory': {300: 42, 301: 58},
        'expected_memory': {302: 100}
    }
    
    # Тест 3: Копирование массива
    test3 = {
        'name': 'Копирование массива из 3 элементов',
        'code': """
            LOAD 500
            STORE 600
            LOAD 501
            STORE 601
            LOAD 502
            STORE 602
        """,
        'init_memory': {500: 10, 501: 20, 502: 30},
        'expected_memory': {600: 10, 601: 20, 602: 30}
    }
    
    return [test1, test2, test3]


if __name__ == "__main__":
    print("=== Утилиты УВМ ===")
    print(f"Размер памяти: {MEMORY_SIZE}")
    print(f"Максимальная константа: {MAX_CONSTANT}")
    print(f"Максимальный адрес: {MAX_ADDRESS:#06x}")
    print(f"Размер команды: {INSTRUCTION_SIZE} байта")
