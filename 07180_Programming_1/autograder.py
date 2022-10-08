import unittest
import map
import readMap
import os


class p1(unittest.TestCase):
    def test(self):
        free1 = map.Free(0, 0)
        free3 = map.Free(0, 0)
        free3.setObstruction(3)
        free9 = map.Free(0, 0)
        free9.setObstruction(9)
        entry = map.Entry(0, 0)
        wall1 = map.Wall(0, 0)
        wall2 = map.Wall(0, 0)

        cells = [wall1, free1, free3, free9, entry, wall2]
        pairs = []
        for (i, cell) in enumerate(cells):
            potential_pairs = cells[i + 1 :]
            for pair in potential_pairs:
                pairs.append((cell, pair))

        student_answers = []
        for pair in pairs:
            student_answers.append(map.obstructionAddition(pair[0], pair[1]))
        reference_answers = [-1, -1, -1, -1, -1, 4, 10, -1, -1, 12, -1, -1, -1, -1, -1]

        for i in range(len(student_answers)):
            if student_answers[i] != reference_answers[i]:
                raise Exception(
                    "\nCell 1: {} \nCell 2: {} \nExpected: {} Got: {}".format(
                        pairs[i][0],
                        pairs[i][1],
                        reference_answers[i],
                        student_answers[i],
                    )
                )


class p2(unittest.TestCase):
    def test(self):
        test_map = readMap.read(os.path.join("maps", "medium.map"))
        entry = map.Entry(16, 6)
        wall = map.Wall(2, 10)
        free = map.Free(5, 5)
        reference_answers = [entry, wall, free]
        student_answers = [
            test_map.getCell(16, 6),
            test_map.getCell(2, 10),
            test_map.getCell(5, 5),
        ]
        student_answers_L = [
            test_map.getCellL(map.Locn(16, 6)),
            test_map.getCellL(map.Locn(2, 10)),
            test_map.getCellL(map.Locn(5, 5)),
        ]

        for (i, student_answer) in enumerate(student_answers):
            if student_answer != reference_answers[i]:
                raise Exception(
                    "\ngetCell Expected: {} Got: {}".format(
                        reference_answers[i], student_answer
                    )
                )

        for (i, student_answer) in enumerate(student_answers_L):
            if student_answer != reference_answers[i]:
                raise Exception(
                    "\ngetCellL Expected: {} Got: {}".format(
                        reference_answers[i], student_answer
                    )
                )


class p3(unittest.TestCase):
    def test(self):
        simple = readMap.read(os.path.join("maps", "simple.map"))
        simple_v2 = readMap.read(os.path.join("maps", "simple_v2.map"))
        medium = readMap.read(os.path.join("maps", "medium.map"))
        medium_v2 = readMap.read(os.path.join("maps", "medium_v2.map"))
        medium_v4 = readMap.read(os.path.join("maps", "medium_v4.map"))

        maps = [simple, simple_v2, medium, medium_v2, medium_v4]
        map_names = ["simple", "simple_v2", "medium", "medium_v2", "medium_v4"]
        reference_answers = [(1, 2), (2, 9), (2, 5), (13, 31), (17, 59)]

        for (i, m) in enumerate(maps):
            student_answer = map.victimSum(m)
            if student_answer != reference_answers[i]:
                raise Exception(
                    "\n{} map Expected: {} Got: {}".format(
                        map_names[i], reference_answers[i], student_answer
                    )
                )


class p4(unittest.TestCase):
    def test(self):
        medium_v4 = readMap.read(os.path.join("maps", "medium_v4.map"))
        agent = map.Agent(medium_v4)
        if agent.allVisited():
            raise Exception(
                "\nagent.all_visited() returned True but not all victims have been visited yet"
            )
        agent.move(map.Locn(4, 18))
        agent.move(map.Locn(2, 5))
        agent.move(map.Locn(2, 11))
        agent.move(map.Locn(11, 20))
        agent.move(map.Locn(2, 17))
        agent.move(map.Locn(11, 26))
        agent.move(map.Locn(2, 5))

        if not agent.allVisited():
            raise Exception(
                "\nagent.all_visited() returned False but all victims have been visited"
            )

        reference_path = [
            map.Locn(16, 6),
            map.Locn(4, 18),
            map.Locn(2, 5),
            map.Locn(2, 11),
            map.Locn(11, 20),
            map.Locn(2, 17),
            map.Locn(11, 26),
            map.Locn(2, 5),
        ]
        if reference_path != agent.path:
            raise Exception(
                "\nWrong path\nExpected: {}\nGot: {}".format(reference_path, agent.path)
            )
