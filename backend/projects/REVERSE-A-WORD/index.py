# Reverse a word
# Accept a word as input from the user and use a loop to reverse it.

word = input("Enter a word: ")
reversed_word = ""

for char in word:
    reversed_word = char + reversed_word

print(f"Reversed word: {reversed_word}")
