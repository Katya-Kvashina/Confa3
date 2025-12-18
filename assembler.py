import sys
import struct
import re
from enum import Enum
from typing import List, Dict, Any, Optional, Tuple


class Opcode(Enum):
    """Коды операций УВМ согласно спецификации"""
    LOAD_CONST = 1      # Загрузка константы (A=1)
    ADD = 3             # Сложение (A=3)
    STORE = 4           # Запись в память (A=4)
    LOAD_MEM = 7        # Чтение из памяти (A=7)


class Instruction:
    """Представление инструкции в промежуточном формате"""
    
    def __init__(self, opcode: Opcode, operand: Optional[int] = None, 
                 label: Optional[str] = None, address: int = 0):
        self.opcode = opcode
        self.operand = operand  # Для LOAD_CONST и STORE
        self.label = label      # Для ссылок на метки
        self.address = address  # Адрес в памяти команд
        self.size = 3           # Все команды 3 байта
        
    def __repr__(self):
        result = f"{self.address:04d}: {self.opcode.name}"
        if self.operand is not None:
            result += f" {self.operand}"
        if self.label:
            result += f" [{self.label}]"
        return result


class BinaryEncoder:
    """Кодирование команд в бинарный формат"""
    
    @staticmethod
    def encode_instruction(instr: Instruction) -> bytes:
        """Кодирование одной инструкции в бинарный формат"""
        opcode = instr.opcode
        
        if opcode == Opcode.LOAD_CONST:
            # Формат: A=1, B=константа (биты 3-11)
            if instr.operand is None:
                raise ValueError("LOAD_CONST требует константу")
            
            value = instr.operand
            # Проверяем диапазон (0-511 для 9 бит)
            if value < 0 or value > 511:
                raise ValueError(f"Константа {value} вне диапазона 0-511")
            
            # Упаковка: биты 0-2: A=1, биты 3-11: константа
            word = (1 << 12) | (value << 3)
            return struct.pack('<I', word)[:3]  # 3 байта
            
        elif opcode == Opcode.STORE:
            # Формат: A=4, B=адрес (биты 3-19)
            if instr.operand is None:
                raise ValueError("STORE требует адрес")
            
            address = instr.operand
            if address < 0 or address > 0xFFFF:
                raise ValueError(f"Адрес {address} вне диапазона 0-65535")
            
            # Упаковка: биты 0-2: A=4, биты 3-19: адрес
            word = (4 << 16) | (address << 3)
            return struct.pack('<I', word)[:3]
            
        elif opcode == Opcode.LOAD_MEM:
            # Формат: A=7, B=0
            return bytes([0x07, 0x00, 0x00])
            
        elif opcode == Opcode.ADD:
            # Формат: A=3, B=0
            return bytes([0x03, 0x00, 0x00])
            
        else:
            raise ValueError(f"Неизвестный opcode: {opcode}")


class Assembler:
    """Основной класс ассемблера"""
    
    def __init__(self):
        self.symbol_table: Dict[str, int] = {}  # Таблица меток
        self.instructions: List[Instruction] = []  # Промежуточное представление
        self.current_address = 0  # Текущий адрес в памяти команд
        self.encoder = BinaryEncoder()
        
    def preprocess_source(self, source: str) -> List[str]:
        """Предварительная обработка исходного кода"""
        lines = []
        for line in source.split('\n'):
            # Удаляем лишние пробелы и комментарии
            line = line.strip()
            if not line:
                continue
                
            # Удаляем комментарии (всё после ;)
            if ';' in line:
                line = line.split(';')[0].strip()
                
            if line:
                lines.append(line)
                
        return lines
    
    def parse_operand(self, operand_str: str) -> Tuple[Optional[int], Optional[str]]:
        """Парсинг операнда, возвращает (число, метка)"""
        operand_str = operand_str.strip()
        
        # Шестнадцатеричное число (0x...)
        if operand_str.startswith('0x'):
            try:
                return int(operand_str, 16), None
            except ValueError:
                raise ValueError(f"Неверный шестнадцатеричный формат: {operand_str}")
        
        # Десятичное число
        if operand_str.isdigit() or (operand_str[0] == '-' and operand_str[1:].isdigit()):
            return int(operand_str), None
        
        # Константа с решёткой (#...)
        if operand_str.startswith('#'):
            num_str = operand_str[1:]
            if num_str.isdigit() or (num_str[0] == '-' and num_str[1:].isdigit()):
                return int(num_str), None
            elif num_str.startswith('0x'):
                try:
                    return int(num_str[2:], 16), None
                except ValueError:
                    # Это может быть метка после решётки
                    return None, num_str
            else:
                # Это может быть метка после решётки
                return None, num_str
        
        # Просто метка
        return None, operand_str
    
    def parse_instruction(self, line: str) -> Optional[Instruction]:
        """Разбор строки ассемблера в промежуточное представление"""
        
        # Проверка на метку
        if line.endswith(':'):
            label = line[:-1].strip()
            if label in self.symbol_table:
                raise ValueError(f"Повторное определение метки: {label}")
            self.symbol_table[label] = self.current_address
            return None
        
        # Разделяем на мнемонику и операнды
        parts = re.split(r'\s+', line, maxsplit=1)
        mnemonic = parts[0].upper()
        
        # Определяем операнд, если есть
        operand = None
        label_ref = None
        
        if len(parts) > 1:
            operand_str = parts[1].strip()
            num_val, label_val = self.parse_operand(operand_str)
            
            if num_val is not None:
                operand = num_val
            elif label_val is not None:
                label_ref = label_val
            else:
                raise ValueError(f"Неверный операнд: {operand_str}")
        
        # Создаем инструкцию
        if mnemonic == "LOAD":
            if operand is not None or label_ref is not None:
                # Загрузка константы
                return Instruction(Opcode.LOAD_CONST, operand, label_ref, self.current_address)
            else:
                # Чтение из памяти (без операнда)
                return Instruction(Opcode.LOAD_MEM, None, None, self.current_address)
        
        elif mnemonic == "STORE":
            if operand is None and label_ref is None:
                raise ValueError("STORE требует операнд")
            return Instruction(Opcode.STORE, operand, label_ref, self.current_address)
        
        elif mnemonic == "ADD":
            return Instruction(Opcode.ADD, None, None, self.current_address)
        
        else:
            raise ValueError(f"Неизвестная мнемоника: {mnemonic}")
    
    def resolve_labels(self):
        """Разрешение ссылок на метки"""
        for instr in self.instructions:
            if instr.label:
                if instr.label not in self.symbol_table:
                    raise ValueError(f"Неопределенная метка: {instr.label}")
                
                # Заменяем ссылку на метку фактическим значением
                instr.operand = self.symbol_table[instr.label]
                instr.label = None
    
    def assemble(self, source: str, test_mode: bool = False) -> List[Instruction]:
        """Основной метод ассемблирования - возвращает промежуточное представление"""
        
        # Сброс состояния
        self.symbol_table.clear()
        self.instructions.clear()
        self.current_address = 0
        
        # Предварительная обработка
        lines = self.preprocess_source(source)
        
        # Первый проход: сбор меток
        for line in lines:
            if line.endswith(':'):
                label = line[:-1].strip()
                if label in self.symbol_table:
                    raise ValueError(f"Повторное определение метки: {label}")
                self.symbol_table[label] = self.current_address
            elif line.strip():
                # Только считаем адреса для не-меток
                self.current_address += 3
        
        # Сброс адреса для второго прохода
        self.current_address = 0
        
        # Второй проход: разбор инструкций
        for line in lines:
            if not line.endswith(':'):  # Пропускаем строки с метками
                instr = self.parse_instruction(line)
                if instr:
                    instr.address = self.current_address
                    self.instructions.append(instr)
                    self.current_address += 3
        
        # Разрешение меток
        self.resolve_labels()
        
        # Проверка диапазонов
        for instr in self.instructions:
            if instr.opcode == Opcode.LOAD_CONST and instr.operand is not None:
                if instr.operand < 0 or instr.operand > 511:
                    raise ValueError(f"Константа {instr.operand} вне диапазона 0-511")
            elif instr.opcode == Opcode.STORE and instr.operand is not None:
                if instr.operand < 0 or instr.operand > 0xFFFF:
                    raise ValueError(f"Адрес {instr.operand} вне диапазона 0-65535")
        
        # Вывод в тестовом режиме
        if test_mode:
            self.print_intermediate_representation()
        
        return self.instructions
    
    def assemble_to_binary(self, source: str, test_mode: bool = False) -> bytes:
        """Ассемблирование с генерацией бинарного кода"""
        intermediate = self.assemble(source, test_mode)
        
        binary_code = bytearray()
        
        for instr in intermediate:
            try:
                binary_instr = self.encoder.encode_instruction(instr)
                binary_code.extend(binary_instr)
                
                if test_mode:
                    hex_bytes = ', '.join(f'0x{b:02X}' for b in binary_instr)
                    print(f"{instr.address:04X}: {hex_bytes}")
                    
            except ValueError as e:
                print(f"Ошибка кодирования: {e}")
                return b''
        
        return bytes(binary_code)
    
    def print_intermediate_representation(self):
        """Вывод промежуточного представления"""
        print("\n=== Промежуточное представление ===")
        print("Адрес | Опкод       | Операнд")
        print("-" * 40)
        
        for instr in self.instructions:
            operand_str = ""
            if instr.operand is not None:
                if instr.opcode == Opcode.LOAD_CONST:
                    operand_str = f"#{instr.operand}"
                else:
                    operand_str = f"0x{instr.operand:04X}"
            
            print(f"{instr.address:04X}  | {instr.opcode.name:<11} | {operand_str}")
        
        if self.symbol_table:
            print("\n=== Таблица меток ===")
            for label, addr in self.symbol_table.items():
                print(f"{label}: 0x{addr:04X}")
    
    def save_to_file(self, binary_data: bytes, filename: str):
        """Сохранение бинарного кода в файл"""
        with open(filename, 'wb') as f:
            f.write(binary_data)
        
        print(f"Бинарный файл сохранён: {filename}")
        print(f"Размер: {len(binary_data)} байт")


def test_specific_sequences():
    """Тестирование конкретных последовательностей из спецификации"""
    
    assembler = Assembler()
    
    print("=== Тестирование последовательностей из спецификации ===")
    
    # Тест 1: LOAD #155 (A=1, B=155)
    print("\n1. Тест загрузки константы #155:")
    test1 = "LOAD #155"
    binary1 = assembler.assemble_to_binary(test1, test_mode=False)
    expected1 = bytes([0x09, 0x04, 0x00])
    print(f"   Получено: {binary1.hex(' ')}")
    print(f"   Ожидается: {expected1.hex(' ')}")
    if binary1 == expected1:
        print("   ✓ СОВПАДАЕТ")
    else:
        print("   ✗ НЕ СОВПАДАЕТ")
    
    # Тест 2: LOAD (чтение из памяти, A=7)
    print("\n2. Тест чтения из памяти (A=7):")
    test2 = "LOAD"
    binary2 = assembler.assemble_to_binary(test2, test_mode=False)
    expected2 = bytes([0x07, 0x00, 0x00])
    print(f"   Получено: {binary2.hex(' ')}")
    print(f"   Ожидается: {expected2.hex(' ')}")
    if binary2 == expected2:
        print("   ✓ СОВПАДАЕТ")
    else:
        print("   ✗ НЕ СОВПАДАЕТ")
    
    # Тест 3: STORE 463 (A=4, B=463)
    print("\n3. Тест записи в память по адресу 463:")
    # Сначала нужно положить значение в стек
    test3 = "LOAD #0\nSTORE 463"
    binary3 = assembler.assemble_to_binary(test3, test_mode=False)
    # Берем только байты команды STORE (последние 3 байта)
    store_bytes = binary3[-3:]
    expected3 = bytes([0x7C, 0x0E, 0x00])
    print(f"   Получено: {store_bytes.hex(' ')}")
    print(f"   Ожидается: {expected3.hex(' ')}")
    if store_bytes == expected3:
        print("   ✓ СОВПАДАЕТ")
    else:
        print("   ✗ НЕ СОВПАДАЕТ")
        # Отладочная информация
        print(f"   Полная последовательность: {binary3.hex(' ')}")
    
    # Тест 4: ADD (A=3)
    print("\n4. Тест сложения (A=3):")
    test4 = "ADD"
    binary4 = assembler.assemble_to_binary(test4, test_mode=False)
    expected4 = bytes([0x03, 0x00, 0x00])
    print(f"   Получено: {binary4.hex(' ')}")
    print(f"   Ожидается: {expected4.hex(' ')}")
    if binary4 == expected4:
        print("   ✓ СОВПАДАЕТ")
    else:
        print("   ✗ НЕ СОВПАДАЕТ")


def main():
    """Основная функция CLI"""
    
    if len(sys.argv) < 3:
        print("Использование:")
        print("  python assembler.py <входной_файл.asm> <выходной_файл.bin> [--test]")
        print("  python assembler.py --test-spec")
        print()
        print("Аргументы:")
        print("  --test      Режим тестирования с выводом промежуточного представления")
        print("  --test-spec Проверка тестовых последовательностей из спецификации")
        return
    
    if sys.argv[1] == "--test-spec":
        test_specific_sequences()
        return
    
    # Обычный режим работы
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    test_mode = "--test" in sys.argv
    
    try:
        # Чтение исходного файла
        with open(input_file, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        # Ассемблирование
        assembler = Assembler()
        
        if test_mode:
            # Получаем промежуточное представление
            print("=== Режим тестирования ===")
            print(f"Исходный файл: {input_file}")
            print("\nИсходный код:")
            print(source_code)
            print("\n" + "="*50)
            
            intermediate = assembler.assemble(source_code, test_mode=True)
            
            # Генерируем бинарный код
            print("\n" + "="*50)
            print("Бинарное представление:")
            binary_data = assembler.assemble_to_binary(source_code, test_mode=True)
            
        else:
            # Просто генерируем бинарный код
            binary_data = assembler.assemble_to_binary(source_code, test_mode=False)
        
        # Сохранение результата
        assembler.save_to_file(binary_data, output_file)
        
    except FileNotFoundError:
        print(f"Ошибка: файл '{input_file}' не найден")
    except ValueError as e:
        print(f"Ошибка ассемблирования: {e}")
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")


if __name__ == "__main__":
    main()
