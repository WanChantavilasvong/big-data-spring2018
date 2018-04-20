#-------------------------------------------
##A. Lists
#A.1 Create a list containing any 4 strings.
list_a = [1, 2, 3, 4]

# EH: these aren't strings - these are integers!

#A.2 Print the 3rd item in the list.
print(list_a[2])

#A.3 Print the 1st and 2nd item int he list using [:] index slicing.
print(list_a[0:2])

#A.4 Add a new string “last” to the end of the list and print the list.
list_a.append("last")
print(list_a)

#A.5 Get the list length and print it.
print(len(list_a))

#A.6 Replace the last item in the list with the string “new” and print
list_a[-1] = "new"
print(list_a[-1])

#-------------------------------------------
##B. Strings
sentence_words = ['I', 'am', 'learning', 'Python', 'to', 'munge', 'large', 'datasets', 'and', 'visualize', 'them']
#B.1 Convert the list into a normal sentence with join(), then print.
print(' '.join(sentence_words))

#B.2 Reverse the order of this list with .reverse(), then print.
sentence_words.reverse()
print(sentence_words)

#B.3 Use the .sort() method using the default sort order.
sentence_words.sort()
print(sentence_words)

#B.4 Use the sorted() function.
##list.sort() changes the list's indices within the list, which means that the original list is now changed.
##sorted(list) is an operand that creates a new list, which means the original list is still intact and that the sorted one can be reassigned to another name.
sorted_words = sorted(sentence_words)
print(sorted_words)

#B.5 Do a case-insensitive alphabetical sort.
#Code adopted from Matthias Eisen, http://matthiaseisen.com/pp/patterns/p0005/
case_insensitive = sorted(sentence_words, key=lambda x: x.lower())
print(case_insensitive)

#-------------------------------------------
##C. Random Function
low = int(input("Lower-bound integer: "))
high = int(input("Higher-bound integer: "))
# I see what you’re doing, but this doesn’t just default to zero – it is always zero. You want to do this in your function defintition (i.e. def randomize(hi, lo = 0): ...
def randomize(lo,hi):
    if lo < 0:
        lo = 0
    from random import randint
    random_num = randint(lo, hi)#inclusive of both numbers
    # These don't test your function - they test the randint function. These should be outside the function definition.
    assert(0 <= random_num <= hi)
    assert(lo <= random_num <= hi)

    return random_num

print(randomize(low,high))

#-------------------------------------------
##D. String Formatting Function
number = input("The position on the best seller list: ")
booktitle = input("Book title: ")

def bestseller(n, book):
    book = book.title()
    message = "The number {} bestseller today is: {}".format(n, book)
    return message

print(bestseller(number, booktitle))

#-------------------------------------------
##E. Password Validation Function
password = str(input("Create new password: "))

# This is not a function!

import string
digit_check = string.digits #0-9
symbol_check = "!?@#$%^&*()-_+="
digit = 0
symbol = 0
upper = 0
password_check = 0

while password_check < 1:
    for i in range(len(password)):
        for j in range(len(digit_check)):
            if password[i] == digit_check[j]:
                digit += 1
        for k in range(len(symbol_check)):
            if password[i] == symbol_check[k]:
                symbol += 1
        if password[i].isupper():
            upper = upper + 1

    if len(password)<8 or len(password)>14:
        print("The password must be 8-14 characters long.")
        password = str(input("Create new password: "))
    elif digit < 2:
        print("The password must include at least 2 numbers.")
        password = str(input("Create new password: "))
    elif upper < 1:
        print("The password must include at least 1 uppercase letter.")
        password = str(input("Create new password: "))
    elif symbol < 1:
        print("The password must include at least 1 of these characters: !?@#$%^&*()-_+= ")
        password = str(input("Create new password: "))
    else:
        password_check += 1
        print("You have successfully created a password!")

#-------------------------------------------
##F. Exponentiation Function
base = int(input("Base integer: "))
expo = int(input("Exponential: "))

def exp (x, y):
    y = y-1
    output = x
    while y > 0:
        output = output*x
        y = y-1
    return output

exp(5,0)

print(exp(base,expo))

#-------------------------------------------
##G. Extra Credit: Min and Max Functions
#List input code adopted from Zach Gates, https://stackoverflow.com/questions/29615274/user-input-integer-list
user_input = input("Enter a series of numbers separated by a single space only: ")
num_list = [int(x) for x in user_input.split(' ')]

def maximum (a):
    imax = 0
    imin = 0
    for i in range(len(num_list)):
        if num_list[i] >= num_list[imax]:
            imax = i
    return str(num_list[imax])

def minimum (b):
    imin = 0
    for i in range(len(num_list)):
        if num_list[i] <= num_list[imin]:
            imin = i
    return str(num_list[imin])

print("The minimum number on the list is: " + maximum(num_list))
print("The minimum number on the list is: " + minimum(num_list))
#
