import classes


class Student(classes.Person):
    def __init__(self, name, age, major, hobby="putting my heart in the work : ^)"):
        super().__init__(name, age, hobby)
        self.major = major

    def introduction(self):
        print(
            "Hi, my name is {}, but you can call me {}. I'm {} years old, majoring in {}, and I like {}.".format(
                self.name, self.nickname, self.age, self.major, self.hobby
            )
        )

    def change_major(self, new_major):
        self.major = new_major


if __name__ == "__main__":
    michael = Student("Michael", 18, "AI", "taking naps")
    michael.set_nickname("Bike")
    betty = Student("Betty", 19, "CS")
    michael.introduction()
    betty.introduction()
    betty.change_major("AI")
    betty.introduction()
