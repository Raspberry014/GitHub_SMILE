function testFunction() {
    alert("Код выполняется!");
}

// 1. Объекты
// 1. Подсчет количества свойств в объекте
function countProperties(obj) {
    return Object.keys(obj).length;
}

const user = { name: "Тимур", age: 23, city: "Павлодар" };
console.log(countProperties(user));

// 2. Проверка наличия свойства в объекте
function hasProperty(obj, key) {
    return obj.hasOwnProperty(key);
}

const user2 = { name: "Данил", age: 25 };
console.log(hasProperty(user2, "age"));
console.log(hasProperty(user2, "city"));

// 3. Объединение двух объектов
function mergeObjects(obj1, obj2) {
    return { ...obj1, ...obj2 };
}

const obj1 = { name: "Тимур", age: 30 };
const obj2 = { age: 20, city: "Алматы" };
console.log(mergeObjects(obj1, obj2));

// 4. Получение всех ключей объекта
function getObjectKeys(obj) {
    return Object.keys(obj);
}

const car = { brand: "Audi", model: "RS6", year: 2024 };
console.log(getObjectKeys(car));

// 5. Удаление свойства из объекта
function removeProperty(obj, key) {
    delete obj[key];
}

const book = { title: "1999", author: "Еркасов Тимур", year: 2001 };
removeProperty(book, "year");
console.log(book);





// 2. Функция
// 1. Функция для вычисления факториала (с использованием рекурсии)
function factorial(n) {
    if (n < 0) return undefined;
    if (n === 0 || n === 1) return 1;
    return n * factorial(n - 1);
}

console.log(factorial(5));
console.log(factorial(0));
console.log(factorial(3));

// 2. Функция для проверки, является ли число простым
function isPrime(n) {
    if (n < 2) return false;
    for (let i = 2; i <= Math.sqrt(n); i++) {
        if (n % i === 0) return false;
    }
    return true;
}

console.log(isPrime(5));
console.log(isPrime(20));
console.log(isPrime(5));

// 3. Функция, возвращающая сумму всех аргументов
function sumAll(...numbers) {
    return numbers.reduce((sum, num) => sum + num, 0);
}

console.log(sumAll(5, 6, 7, 8));
console.log(sumAll(50, 100, 150));
console.log(sumAll());

// 4. Функция, которая переворачивает строку
function reverseString(str) {
    return str.split('').reverse().join('');
}

console.log(reverseString("lenovo"));
console.log(reverseString("Visual Studio Code"));

// 5. Функция, которая форматирует имя
function formatName(name) {
    if (!name) return '';
    return name.charAt(0).toUpperCase() + name.slice(1).toLowerCase();
}

console.log(formatName("даУЛЕТ"));
console.log(formatName("ТИМ"));
console.log(formatName("арман"));




// 3. Массив
// 1. Функция для нахождения максимального элемента в массиве
function findMax(arr) {
    if (arr.length === 0) return undefined;
    return Math.max(...arr);
}

console.log(findMax([3, 5, 22, 11, 1]));
console.log(findMax([-5, -88, -12, -9]));
console.log(findMax([150]));

// 2. Функция для фильтрации четных чисел из массива
function filterEvenNumbers(arr) {
    return arr.filter(num => num % 2 === 0);
}

console.log(filterEvenNumbers([1, 2, 3, 4, 5, 6]));
console.log(filterEvenNumbers([7, 9, 11]));
console.log(filterEvenNumbers([8, 13, 15, 22, 44]));

// 3. Функция для объединения двух массивов без дубликатов
function mergeUnique(arr1, arr2) {
    return [...new Set([...arr1, ...arr2])];
}

console.log(mergeUnique([3, 4, 5], [1, 2, 3]));
console.log(mergeUnique([10, 9], [8, 7, 6]));
console.log(mergeUnique([1, 2, 3], []));

// 4. Функция для переворота массива
function reverseArray(arr) {
    return [...arr].reverse();
}

console.log(reverseArray([1, 2, 3]));
console.log(reverseArray(["T", "I", "M"]));
console.log(reverseArray([true, false, true]));

// 5. Функция для поиска индекса элемента в массиве
function findIndex(arr, value) {
    return arr.indexOf(value);
}

console.log(findIndex([10, 50, 60, 20], 20));
console.log(findIndex(["банан", "вишня", "апельсин"], "вишня"));
console.log(findIndex([4, 5, 3], 1));
