from functions import add_o


class Person:
    def __init__(self, name, age, hobby="taking long walks on the beach"):
        self.name = name
        self.nickname = add_o(name)
        self.age = age
        self.hobby = hobby

    def set_nickname(self, nickname):
        self.nickname = nickname

    def introduction(self):
        print(
            "Hi, my name is {}, but you can call me {}. I'm {} years old and I like {}.".format(
                self.name, self.nickname, self.age, self.hobby
            )
        )
