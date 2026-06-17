Python Interview Questions & Answers

1. What is a Dictionary?

A dictionary is a collection of key-value pairs.

my_dict = {
    "A": 100,
    "B": 200,
    "C": 300
}

---

2. How do you add a key to a dictionary?

my_dict["D"] = 400

---

3. How do you swap keys and values in a dictionary?

my_dict = {
    "A": 100,
    "B": 200,
    "C": 300
}

swapped = {v: k for k, v in my_dict.items()}
print(swapped)

Output:

{
    100: "A",
    200: "B",
    300: "C"
}

---

4. How do you get the sum of all values in a dictionary?

total = sum(my_dict.values())
print(total)

Output:

600

---

5. Count Binary Transitions

Problem

Count transitions between adjacent bits.

Example:

1100100

Transitions:

1→0
0→1
1→0

Total = 3

Solution

def count_transitions(binary):
    count = 0

    for i in range(1, len(binary)):
        if binary[i] != binary[i - 1]:
            count += 1

    return count

---

6. Determine if Binary Has More Than One Transition

def is_valid(binary):
    return count_transitions(binary) > 1

Examples:

1100100 → True
1111000 → False
1010100 → True
0000111 → False
1111111 → False
0000000 → False

---

String Problems

7. First Non-Repeating Character

Problem

Input:

"swiss"

Output:

"w"

Solution

from collections import Counter

def first_unique(s):
    counts = Counter(s)

    for ch in s:
        if counts[ch] == 1:
            return ch

    return None

Time Complexity

O(n)

---

8. Longest Substring Without Repeating Characters

Problem

Input:

"abcabcbb"

Output:

3

Solution

def longest_substring(s):
    seen = set()
    left = 0
    max_len = 0

    for right in range(len(s)):

        while s[right] in seen:
            seen.remove(s[left])
            left += 1

        seen.add(s[right])

        max_len = max(
            max_len,
            right - left + 1
        )

    return max_len

Time Complexity

O(n)

Space Complexity

O(n)

---

OOP in Python

9. What is a Class?

A class is a blueprint used to create objects.

class Person:
    pass

---

10. What is an Object?

An object is an instance of a class.

p1 = Person()

---

11. Create a Person Class

class Person:

    def __init__(self, name, age):
        self.name = name
        self.age = age

    def display(self):
        print(f"Name: {self.name}, Age: {self.age}")

p1 = Person("Vamsi", 28)
p1.display()

---

12. What is "__init__"?

"__init__" is a constructor.

It is automatically called whenever an object is created.

Example:

class Person:

    def __init__(self, name):
        self.name = name

p1 = Person("Vamsi")

Internally Python executes:

Person.__init__(p1, "Vamsi")

---

13. What is "self"?

"self" refers to the current object instance.

Example:

class Person:

    def __init__(self, name):
        self.name = name

When:

p1 = Person("Vamsi")

Then:

self.name

means:

p1.name

---

14. Why is "self" Needed?

Wrong:

class Person:

    def __init__(self, name):
        name = name

The value is not stored in the object.

Correct:

class Person:

    def __init__(self, name):
        self.name = name

---

15. What Happens Without "self"?

Wrong:

class Person:

    def display():
        print("Hello")

Calling:

p1 = Person()
p1.display()

Results in:

TypeError: display() takes 0 positional arguments but 1 was given

Reason:

Python internally does:

Person.display(p1)

and automatically passes the object.

---

16. Instance Method

class Person:

    def display(self):
        print(self.name)

Uses object data through "self".

---

17. Static Method

class Person:

    @staticmethod
    def greet():
        print("Hello")

Usage:

Person.greet()

Output:

Hello

---

18. Explain This Class

class Person:

    def __init__(self, name, age):
        self.name = name
        self.age = age

    def print_details(self):
        print(f"{self.age} : {self.name}")

Create object:

p1 = Person("Vijay", 25)

Call method:

p1.print_details()

Output:

25 : Vijay

---

Frequently Asked Interview Questions

1. What is a dictionary?
2. Difference between list, tuple, set, and dictionary?
3. How do you swap dictionary keys and values?
4. How do you get the sum of dictionary values?
5. What is Counter in Python?
6. Find the first non-repeating character in a string.
7. Find the longest substring without repeating characters.
8. What is a class?
9. What is an object?
10. What is "__init__"?
11. What is "self"?
12. Why is "self" required?
13. What happens if "self" is omitted?
14. What is an instance method?
15. What is a static method?
16. Explain encapsulation.
17. Explain inheritance.
18. Explain polymorphism.
19. Explain abstraction.
20. What is MRO (Method Resolution Order)?