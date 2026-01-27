import numpy as np

alphabets = {
    "RU": "АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ",
    "EN": "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
}

def to_numbers(text, alpha):
    return [alpha.index(c) for c in text.upper() if c in alpha]

def to_text(nums, alpha):
    return ''.join(alpha[n % len(alpha)] for n in nums)

def inverse_mod(a, m):
    for x in range(1, m):
        if (a * x) % m == 1:
            return x
    raise Exception("Нет обратного элемента")

def invert_matrix(matrix, mod):
    det = int(round(np.linalg.det(matrix)))
    det_inv = inverse_mod(det % mod, mod)
    adj = np.round(det * np.linalg.inv(matrix)).astype(int)
    return (det_inv * adj) % mod

def encrypt(msg, key, alpha):
    nums = to_numbers(msg, alpha)
    n = len(key)
    while len(nums) % n != 0:
        nums.append(alpha.index(alpha[-1]))
    result = []
    for i in range(0, len(nums), n):
        block = np.array(nums[i:i+n])
        res = np.dot(key, block) % len(alpha)
        result.extend(res)
    return to_text(result, alpha)

def decrypt(cipher, key, alpha):
    inv_key = invert_matrix(key, len(alpha))
    nums = to_numbers(cipher, alpha)
    n = len(inv_key)
    result = []
    for i in range(0, len(nums), n):
        block = np.array(nums[i:i+n])
        res = np.dot(inv_key, block) % len(alpha)
        result.extend(res)
    return to_text(result, alpha)

def input_matrix():
    size = int(input("Размер матрицы (n): "))
    print(f"Введите {size} строк по {size} чисел:")
    mat = []
    for i in range(size):
        row = input(f"{i+1}: ").split()
        mat.append([int(x) for x in row])
    return np.array(mat)

# основной запуск
if __name__ == "__main__":
    lang = input("Язык (RU/EN): ").strip().upper()
    if lang not in alphabets:
        lang = "RU"
    alpha = alphabets[lang]

    print("Алфавит:", alpha)
    text = input("Сообщение: ").upper()
    matrix = input_matrix()

    enc = encrypt(text, matrix, alpha)
    dec = decrypt(enc, matrix, alpha)

    print("Зашифровано:", enc)
    print("Расшифровано:", dec)
