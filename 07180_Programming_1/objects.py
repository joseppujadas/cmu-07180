import classes

if __name__ == "__main__":
    michael = classes.Person("Michael", 18, "taking naps")
    michael.set_nickname("Bike")
    betty = classes.Person("Betty", 19)
    michael.introduction()
    betty.introduction()
