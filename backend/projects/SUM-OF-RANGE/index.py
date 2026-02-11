# Sum of a range
# Use a while loop to calculate the sum of all numbers from 1 to a given integer, n.

n = int(input("Enter a number: "))
sum = 0
counter = 1

while counter <= n:
    sum += counter
    counter += 1

print(f"Sum of numbers from 1 to {n} is: {sum}")
