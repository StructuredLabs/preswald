import pandas as pd

from preswald import text


text("# Welcome to Preswald!")
text("This is your first app. 🎉")

# Testing strings
text("Testing string:")
test = "Hello, Preswald!"
text(test)

# Testing numbers
text("Testing number:")
test = 42
text(test)

text("Testing float:")
test = 42.033445
text(test)

# Testing lists of strings
text("Testing list of strings:")
test = ["apple", "banana", "cherry"]
text(test)

# Testing lists of numbers
text("Testing list of numbers:")
test = [10, 20, 30]
text(test)

text("Testing list of floats:")
test = [10.1232, 20.5432, 30.5324]
text(test)

# Testing dictionaries
text("Testing dictionary:")
test = {"name": "Alice", "age": 30, "city": "Wonderland"}
text(test)

# Testing tuples
text("Testing tuple:")
test = (1, 2, 3)
text(test)

# Testing sets
text("Testing set:")
test = {"apple", "banana", "cherry"}
text(test)

# Testing boolean values
text("Testing boolean True:")
test = True
text(test)

text("Testing boolean False:")
test = False
text(test)

# Testing None
text("Testing None:")
test = None
text(test)

# Testing nested lists
text("Testing nested list:")
test = [[1, 2], [3, 4], [5, 6]]
text(test)

# Testing nested dictionaries
text("Testing nested dictionary:")
test = {"key1": {"subkey1": 1, "subkey2": 2}, "key2": {"subkey3": 3}}
text(test)

# Testing mixed data types in a list
text("Testing mixed data types in a list:")
test = [1, "two", 3.0, True, None]
text(test)

# Testing mixed data types in a dictionary
text("Testing mixed data types in a dictionary:")
test = {"integer": 1, "string": "two", "float": 3.0, "boolean": True, "none": None}
text(test)

# THESE SHOULD NOT WORK
text("Printing empty dataframe")
test = pd.DataFrame()
text(test)

text("Printing dataframe with columns only")
test = pd.DataFrame(columns=["A", "B", "C"])
text(test)

text("Printing dataframe with data")
test = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6], "C": [7, 8, 9]})
text(test)

text("Printing dataframe with mixed data types")
test = pd.DataFrame({"A": [1, "two", 3.0], "B": [4.5, None, 6], "C": ["seven", 8, 9]})
text(test)

text("Printing large dataframe")
test = pd.DataFrame({"A": range(1, 101), "B": range(101, 201), "C": range(201, 301)})
text(test)
