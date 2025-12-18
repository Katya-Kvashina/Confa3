import sys
import struct
from enum import Enum
from typing import List, Tuple, Dict, Any

class Opcode(Enum):
    """Коды операций УВМ"""
    LOAD_CONST = 1      # Загрузка константы
    STORE = 4           # Запись в память
    LOAD_MEM = 7        # Чтение из памяти
    ADD = 3             # Сложение
    
class Assembler:
    def __init__(self):
        self.labels = {}
        self.symbol_table = {}
        
    def parse_instruction(self, line: str, line_num: int) -> Dict[str, Any]:
        """Разбор одной инструкции ассемблера"""
        line = line.strip()
        
        # Пропускаем пустые строки и комментарии
        if not line or line.startswith(';'):
            return None
            
        # Удаляем комментарий в конце строки
        if ';' in line:
            line = line.split(';')[0].strip()
            
        parts = line.split()
        if not parts:
            return None
            
        op = parts[0].upper()
        
        # Обработка директив и меток
        if op.endswith(':'):
            self.labels[op[:-1]] = line_num
            return None
            
        # Парсинг инструкций
        if op == 'LOAD':
            if len(parts) != 2:
                raise ValueError(f"Ошибка в строке {line_num}: LOAD требует один аргумент")
            
            # Проверяем, является ли аргумент константой
            if parts[1].startswith('#') or parts[1].isdigit():
                # Загрузка константы
                value = int(parts[1].replace('#', ''))
                return {
                    'opcode': Opcode.LOAD_CONST,
                    'value': value,
                    'size': 3
                }
            else:
                # Загрузка из памяти по адресу в стеке
                return {
                    'opcode': Opcode.LOAD_MEM,
                    'size': 3
                }
                
        elif op == 'STORE':
            if len(parts) != 2:
                raise ValueError(f"Ошибка в строке {line_num}: STORE требует один аргумент")
            
            # Запись в память по указанному адресу
            addr = self.parse_operand(parts[1])
            return {
                'opcode': Opcode.STORE,
                'address': addr,
                'size': 3
            }
            
        elif op == 'ADD':
            # Сложение: второй операнд из стека, первый из памяти
            return {
                'opcode': Opcode.ADD,
                'size': 3
            }
            
        else:
            raise ValueError(f"Неизвестная инструкция: {op}")
    
    def parse_operand(self, operand: str) -> int:
        """Парсинг операнда (число или метка)"""
        if operand.isdigit():
            return int(operand)
        elif operand.startswith('0x'):
            return int(operand[2:], 16)
        elif operand in self.labels:
            return self.labels[operand]
        else:
            raise ValueError(f"Неизвестный операнд: {operand}")
    
    def assemble(self, source_path: str, output_path: str, test_mode: bool = False) -> List[Dict]:
        """Основной метод ассемблирования"""
        
        # Чтение исходного файла
        with open(source_path, 'r', encoding='utf-8') as f:
            source_lines = f.readlines()
        
        # Первый проход: сбор меток
        intermediate = []
        for i, line in enumerate(source_lines):
            try:
                instr = self.parse_instruction(line, len(intermediate))
                if instr:
                    intermediate.append(instr)
            except ValueError as e:
                print(f"Ошибка в строке {i+1}: {e}")
                return []
        
        # Вывод промежуточного представления в тестовом режиме
        if test_mode:
            print("Промежуточное представление:")
            for i, instr in enumerate(intermediate):
                print(f"{i:03d}: {instr}")
        
        return intermediate

def main():
    if len(sys.argv) < 3:
        print("Использование: python assembler.py <входной_файл> <выходной_файл> [--test]")
        return
    
    source_file = sys.argv[1]
    output_file = sys.argv[2]
    test_mode = '--test' in sys.argv
    
    assembler = Assembler()
    intermediate = assembler.assemble(source_file, output_file, test_mode)
    
    # Сохранение промежуточного представления
    if intermediate:
        print(f"\nУспешно ассемблировано: {len(intermediate)} инструкций")
        # Здесь будет запись в бинарный файл на этапе 2

if __name__ == "__main__":
    main()
