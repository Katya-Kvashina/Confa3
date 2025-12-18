import sys
import struct
import csv
from enum import Enum

class Opcode(Enum):
    LOAD_CONST = 1
    STORE = 4
    LOAD_MEM = 7
    ADD = 3

class UVMInterpreter:
    def __init__(self, memory_size=65536):
        self.memory = [0] * memory_size  # Память данных
        self.code_memory = []           # Память команд
        self.stack = []                 # Стек УВМ
        self.pc = 0                     # Счетчик команд
        self.running = False
        
    def load_binary(self, binary_path: str):
        """Загрузка бинарной программы"""
        with open(binary_path, 'rb') as f:
            data = f.read()
        
        # Загружаем команды по 3 байта
        for i in range(0, len(data), 3):
            chunk = data[i:i+3]
            if len(chunk) == 3:
                self.code_memory.append(chunk)
        
        print(f"Загружено {len(self.code_memory)} команд")
    
    def decode_instruction(self, instr_bytes: bytes) -> Dict:
        """Декодирование бинарной команды"""
        if len(instr_bytes) != 3:
            return None
        
        # Извлекаем поле A (биты 0-2)
        a_field = instr_bytes[0] & 0x07
        
        # Извлекаем поле B (биты 3-19)
        b_field = ((instr_bytes[2] << 16) | (instr_bytes[1] << 8) | instr_bytes[0]) >> 3
        
        opcode = Opcode(a_field)
        
        return {
            'opcode': opcode,
            'b_field': b_field,
            'raw': instr_bytes
        }
    
    def execute_load_const(self, b_field: int):
        """Выполнение загрузки константы"""
        self.stack.append(b_field)
        print(f"LOAD_CONST: загружена константа {b_field}, размер стека: {len(self.stack)}")
    
    def execute_store(self, b_field: int):
        """Выполнение записи в память"""
        if not self.stack:
            raise RuntimeError("Стек пуст при выполнении STORE")
        
        value = self.stack.pop()
        if 0 <= b_field < len(self.memory):
            self.memory[b_field] = value
            print(f"STORE: записано значение {value} по адресу {b_field}")
        else:
            raise RuntimeError(f"Недопустимый адрес памяти: {b_field}")
    
    def execute_load_mem(self):
        """Выполнение чтения из памяти"""
        if not self.stack:
            raise RuntimeError("Стек пуст при выполнении LOAD_MEM")
        
        address = self.stack.pop()
        if 0 <= address < len(self.memory):
            value = self.memory[address]
            self.stack.append(value)
            print(f"LOAD_MEM: прочитано значение {value} из адреса {address}")
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
        
        if 0 <= address < len(self.memory):
            op1 = self.memory[address]
            result = op1 + op2
            self.stack.append(result)
            print(f"ADD: {op1} + {op2} = {result} (адрес: {address})")
        else:
            raise RuntimeError(f"Недопустимый адрес памяти: {address}")
    
    def run(self):
        """Основной цикл выполнения"""
        self.running = True
        self.pc = 0
        
        while self.running and self.pc < len(self.code_memory):
            instr_bytes = self.code_memory[self.pc]
            instr = self.decode_instruction(instr_bytes)
            
            if not instr:
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
                    
            except RuntimeError as e:
                print(f"Ошибка выполнения: {e}")
                break
            
            self.pc += 1
        
        print(f"\nВыполнение завершено. PC={self.pc}")
    
    def save_memory_dump(self, output_path: str, start_addr: int, end_addr: int):
        """Сохранение дампа памяти в CSV"""
        if start_addr < 0 or end_addr > len(self.memory) or start_addr >= end_addr:
            raise ValueError("Некорректный диапазон адресов")
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Адрес', 'Значение'])
            
            for addr in range(start_addr, end_addr):
                writer.writerow([addr, self.memory[addr]])
        
        print(f"Дамп памяти сохранен в {output_path} ({end_addr-start_addr} записей)")

def main():
    if len(sys.argv) < 4:
        print("Использование: python interpreter.py <бинарный_файл> <выходной_csv> <начальный_адрес> <конечный_адрес>")
        return
    
    binary_file = sys.argv[1]
    output_csv = sys.argv[2]
    start_addr = int(sys.argv[3])
    end_addr = int(sys.argv[4])
    
    interpreter = UVMInterpreter()
    interpreter.load_binary(binary_file)
    interpreter.run()
    interpreter.save_memory_dump(output_csv, start_addr, end_addr)

if __name__ == "__main__":
    main()
