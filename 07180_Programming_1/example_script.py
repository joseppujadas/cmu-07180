# look at me I'm a comment!
menu = ["pizza", "pasta", "potato", "peanut butter"]

"""
wow I'm on
multiple lines now
"""
prices = {}
for food_item in menu:
    prices[food_item] = len(food_item)

for food_item in prices:
    if prices[food_item] < 6:
        print(food_item + " looks pretty good, let's buy some!")
