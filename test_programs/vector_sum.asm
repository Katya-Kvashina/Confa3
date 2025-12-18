; Сложение вектора длины 7 с константой 157
; Исходный вектор: адреса 100-106
; Результат: адреса 200-206

; Инициализация данных (в интерпретаторе нужно предварительно заполнить memory[100-106])

; Элемент 0: memory[100] + 157 -> memory[200]
LOAD 100
LOAD #157
ADD
STORE 200

; Элемент 1: memory[101] + 157 -> memory[201]
LOAD 101
LOAD #157
ADD
STORE 201

; Элемент 2: memory[102] + 157 -> memory[202]
LOAD 102
LOAD #157
ADD
STORE 202

; Элемент 3: memory[103] + 157 -> memory[203]
LOAD 103
LOAD #157
ADD
STORE 203

; Элемент 4: memory[104] + 157 -> memory[204]
LOAD 104
LOAD #157
ADD
STORE 204

; Элемент 5: memory[105] + 157 -> memory[205]
LOAD 105
LOAD #157
ADD
STORE 205

; Элемент 6: memory[106] + 157 -> memory[206]
LOAD 106
LOAD #157
ADD
STORE 206

; Конец программы
