def add_o(str):
    new_str = str + "o"
    return new_str


if __name__ == "__main__":
    names = ["Adam", "Betty", "Carl", "Dorothy"]
    nicknames = {}
    for name in names:
        nicknames[name] = add_o(name)
    print(nicknames)
