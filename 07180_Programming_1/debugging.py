import pdb


def mystery():
    a = [1, 2, 3]
    b = [3, 2, 1]
    b[2] = 2
    pdb.set_trace()
    print(a + b)
