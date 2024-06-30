def find_common_elements(listA, listB):
    return list(set(listA) & set(listB))

# Example usage
listA = ["pizza", "tomato sauce", "pepperoni", "restaurant"]
listB = ["pizza", "tomato", "peperone", "restaurant"]
listC = find_common_elements(listA, listB)
print(listC)  # Output: ["pizza", "restaurant"]

