import pickle
import random
import argparse
import math
import numpy as np
import readMap
import search
import SAR
import simulate
from params import *
import decisionTree as DT
import neuralNet as NN
import classification as CF
import utils

debugging = False  # True

mapNames = [
    "maps/simple.map",
    "maps/simple_v2.map",
    "maps/medium.map",
    "maps/medium_v2.map",
    "maps/medium_v4.map",
]


class TestHW4:
    def __init__(self, goalType=None, mapName=None):
        self.num = self.correct = self.total_num = self.total_correct = 0
        self.goalTypes = [goalType] if goalType else GoalTypes
        self.mapNames = [mapName] if mapName else mapNames

    def begin_generation(self, description):
        print("Generating refsol for %s" % description)
        self.tests = {}
        self.file_name = "autograder_files/" + description.replace(" ", "_") + ".pk"

    def end_generation(self):
        with open(self.file_name, "wb") as pkf:
            pickle.dump(self.tests, pkf)

    def begin_test(self, problem, step, description):
        print("Testing Problem %d, step %d (%s)" % (problem, step, description))
        file_name = "autograder_files/" + description.replace(" ", "_") + ".pk"
        with open(file_name, "rb") as pkf:
            self.tests = pickle.load(pkf)
        self.problem = problem
        self.step = step

    def end_test(self):
        print(
            "\nScore for Problem %d, step %d: %d out of %d\n"
            % (self.problem, self.step, self.correct, self.num)
        )
        self.total_num += self.num
        self.total_correct += self.correct

    def doit(self, problem, step=1):
        fn = getattr(
            type(self),
            "%s_p%d_s%d" % ("generate" if generating else "test", problem, step),
        )
        self.num = self.correct = 0
        fn(self)

    ##########  END OF UTILITY FUNCTIONS ##########


    def test_p1_s1(self):  # info gain
        self.begin_test(1, 1, "info gain")
        with open("autograder_files/decisionTreeData.pk", "rb") as pkf:
            treeData = pickle.load(pkf)
        for name in treeData["names"]:
            dt = treeData[(name, "tree")]
            infoGains = self.tests[(name, "infoGains")]
            for refGain, feature, data in infoGains:
                self.num += 1
                stuGain = dt.infoGain(feature, data)
                if abs(refGain - stuGain) <= 1e-5:
                    self.correct += 1
                    print(
                        "Correct info gain (%.3f) for '%s' and %d datums"
                        % (stuGain, feature, len(data))
                    )
                else:
                    print(
                        "Incorrect info gain for '%s' (index %d) and data"
                        % (feature, dt.getFeatures().index(feature))
                    )
                    for datum in data:
                        print(" ", datum)
                    print("  Refsol: %f" % refGain)
                    print("  Yours:  %f" % stuGain)
        self.end_test()


    def test_p1_s2(self):  # create tree
        self.begin_test(1, 2, "create tree")
        with open("autograder_files/decisionTreeData.pk", "rb") as pkf:
            treeData = pickle.load(pkf)
        for name in treeData["names"]:
            pclass = treeData.get((name, "pclass"))
            feature_values = treeData[(name, "feature_values")]
            classes = treeData[(name, "classes")]
            self.num += 4
            for skip in range(1, 5):
                ref_acc, train, test = self.tests[(name, skip)]
                if skip == 1:
                    print("\nValidating tree trained and tested on full dataset")
                else:
                    print(
                        "\nValidating tree trained on %.0f%% of full dataset and tested on rest of data"
                        % (100 * len(train) / (len(train) + len(test)))
                    )
                stu_dt = DT.DecisionTree(feature_values, classes)
                stu_dt.createTree(train)
                if skip == 1 and not utils.compareTrees(
                    treeData[(name, "tree")], stu_dt, debugging
                ):
                    print("Your decision tree does not match the refsol:")
                    treeData[(name, "tree")].display(2)
                    print("Yours:")
                    stu_dt.display(2)
                    break

                stu_acc = utils.validateDT(stu_dt, test, pclass, debugging)
                if (stu_acc > ref_acc) or abs(stu_acc - ref_acc) < 1e-5:
                    self.correct += 1
                    if ref_acc == 1:
                        print("Accuracy matches refsol")
                    else:
                        print(
                            "Accuracy matches refsol (%.1f%%), although both have misclassifications"
                            % (100 * stu_acc)
                        )
                else:
                    print(
                        "Accuracy (%.1f%) less than refsol (%.1f%)"
                        % (100 * stu_acc, 100 * ref_acc)
                    )
        self.end_test()


    def test_p1_s3(self):  # prune
        self.begin_test(1, 3, "prune")
        with open("autograder_files/decisionTreeData.pk", "rb") as pkf:
            treeData = pickle.load(pkf)
        for name in treeData["names"]:
            classes = treeData[(name, "classes")]
            feature_values = treeData[(name, "feature_values")]
            dataset = treeData[(name, "dataset")]
            tree = treeData[(name, "tree")]
            if debugging:
                print(name, "full")
                tree.display(2)

            for i in range(len(feature_values), 0, -1):
                self.num += 1
                tree = DT.DecisionTree(feature_values, classes)
                tree.createTree(dataset)
                tree.prune(dataset, i)
                ref_tree = self.tests[(name, i)]
                if utils.compareTrees(ref_tree, tree, debugging):
                    print(
                        "Pruned tree for '%s' domain to depth %d matches refsol!"
                        % (name, i)
                    )
                    self.correct += 1
                else:
                    print(
                        "Pruned tree for '%s' domain to depth %d does NOT match refsol:"
                        % (name, i)
                    )
                    ref_tree.display(2)
                    print("Yours:")
                    tree.display(2)
                    print()
        self.end_test()


    def test_p2_s1(self):  # feed forward"
        self.begin_test(2, 1, "feed forward")
        nn = self.tests["net"]
        self.num = 1
        self.correct = 1
        output = nn.feed_forward(self.tests["input"])
        if np.max(np.abs(output - self.tests["ins"][-1])) > 1e-5:
            print("Output differs from refsol: %s" % self.tests["ins"][-1])
            print("  Yours: %s" % output)
            self.correct = 0
        for i in range(len(nn.ins) - 1):
            if np.max(np.abs(nn.ins[i] - self.tests["ins"][i])) > 1e-5:
                print(
                    "Inputs to layer %d differs from refsol: %s"
                    % (i + 1, self.tests["ins"][i])
                )
                print("  Yours: %s" % nn.ins[i])
                self.correct = 0
        for i in range(len(nn.ins) - 1):
            if np.max(np.abs(nn.outs[i] - self.tests["outs"][i])) > 1e-5:
                print(
                    "Outputs from layer %d differs from refsol: %s"
                    % (i + 1, self.tests["outs"][i])
                )
                print("  Yours: %s" % nn.outs[i])
                self.correct = 0
        self.end_test()


    def test_p2_s2(self):  # neural nets
        self.begin_test(2, 2, "neural nets")
        with open("autograder_files/neuralNetData.pk", "rb") as pkf:
            netData = pickle.load(pkf)

        for name in ["fixStreet", "images"]:
            self.num += 1
            ref_accuracy, layers, epochs, lr, nfold = self.tests[name]
            net = NN.trainNetwork(
                netData[(name, "training")], layers, epochs, lr, nfold
            )
            stu_accuracy = (
                utils.validateNN(net, netData[(name, "testing")]) if net else 0
            )
            if stu_accuracy >= ref_accuracy:
                print(
                    "You met, or exceeded, the refsol's accuracy in the '%s' domain (%.3f vs %.3f)"
                    % (name, ref_accuracy, stu_accuracy)
                )
                self.correct += 1
            elif stu_accuracy >= 0.95 * ref_accuracy:
                print(
                    "You got within 5%% of the refsol's accuracy in the '%s' domain:"
                    % name
                )
                print("   Refsols: %.3f; Yours: %.3f)" % (ref_accuracy, stu_accuracy))
                self.correct += 1
            else:
                print(
                    "You were not within 5%% of the refsol's accuracy in the '%s' domain:"
                    % name
                )
                print("   Refsols: %.3f; Yours: %.3f)" % (ref_accuracy, stu_accuracy))
        self.end_test()


    def test_p3_s1(self):  # obstacle classifier
        self.begin_test(3, 1, "obstacle classifier")
        self.num = 1
        fv = self.tests["feature_values"]
        cl = self.tests["classes"]
        trainData = self.tests["trainData"]
        testData = self.tests["testData"]
        dt = CF.trainObstacleCost(fv, cl, trainData)
        accuracy = utils.validateDT(dt, testData) if dt else 0
        if accuracy >= 0.95:
            print(
                "Your obstacle cost decision tree has %.0f%% accuracy on the unseen test data"
                % (accuracy * 100)
            )
            print("   Congrats!")
            self.correct = 1
        elif accuracy >= 0.9:
            print(
                "Your obstacle cost decision tree has %.0f%% accuracy on the unseen test data"
                % (accuracy * 100)
            )
            print("  Pretty good, but you can probably do better")
            self.correct = 1
        else:
            print(
                "Your obstacle cost decision tree has only %.0f%% accuracy on the unseen test data"
                % (accuracy * 100)
            )
            print("  Keep trying")
        self.end_test()


    def test_p3_s2(self):  # isVictim classifier
        self.begin_test(3, 2, "isVictim classifier")
        self.num = 1
        trainData = self.tests["trainData"]
        testData = self.tests["testData"]
        nn = CF.trainIsVictim(trainData)
        accuracy = utils.validateNN(nn, testData) if nn else 0
        if accuracy >= 0.9:
            print(
                "Your isVictim neural net has %.0f%% accuracy on the unseen test data"
                % (accuracy * 100)
            )
            print("   Congrats!")
            self.correct = 1
        elif accuracy >= 0.85:
            print(
                "Your isVictim neural net has %.0f%% accuracy on the unseen test data"
                % (accuracy * 100)
            )
            print("  Pretty good, but you can probably do better")
            self.correct = 1
        else:
            print(
                "Your isVictim neural net has only %.0f%% accuracy on the unseen test data"
                % (accuracy * 100)
            )
            print("  Keep trying")
        self.end_test()


class TestIntegration(TestHW4):
    def __init__(self, goalType, map, useGraphics, maxSteps, simSpeed=0.1):
        super().__init__(goalType, map)
        self.useGraphics = useGraphics
        self.maxSteps = maxSteps
        self.simSpeed = simSpeed

    def split_data(self, dataset, classes):
        random.shuffle(dataset)
        splitData = {}
        for classs in classes:
            splitData[classs] = [0, [data[1] for data in dataset if data[0] == classs]]
        return splitData

    def get_next_datum(self, data_count):
        # First item is an index, second is the data itself
        # print(data_count[0], len(data_count[1]))
        datum = data_count[1][data_count[0]]
        data_count[0] += 1
        return datum

    def update_map(self, theMap, obstacleTree, victimNet, dtData, nnData):
        obstacleData = self.split_data(dtData[("testData")] * 100, dtData[("classes")])
        victimData = self.split_data(nnData[("testData")] * 10, (0, 1))

        print("Original map:")
        theMap.display()
        victimsList = []
        misclassifications = False
        cellCount = 0
        # To minimize false positives, test on only 10% of free, non-victim cells
        skipCells = int(0.5 + theMap.numRows() * theMap.numCols() * 0.1)
        print(skipCells)
        for r in range(theMap.numRows()):
            for c in range(theMap.numCols()):
                cellCount += 1
                cell = theMap.getCell(r, c)
                if cell and cell.isFree():
                    cost = cell.getObstruction()
                    pred_cost = int(
                        obstacleTree.classify(
                            self.get_next_datum(obstacleData[str(cost)])
                        )
                    )
                    if pred_cost != cost:
                        print(
                            "Misclassified obstruction cost at %s: Refsol: %d; Yours: %d"
                            % (cell.getLocn(), cost, pred_cost)
                        )
                        misclassifications = True
                        cell.setObstruction(pred_cost)

                    isVictim = cell.isVictim()
                    # To minimize false positives, test on only 10% of free, non-victim cells
                    if isVictim or cellCount % skipCells == 0:
                        pred_isVictim = victimNet.classify(
                            self.get_next_datum(victimData[isVictim])
                        )
                        if pred_isVictim:
                            victimsList += [cell.getLocn()]
                        if pred_isVictim != isVictim:
                            print(
                                "Misclassified victim at %s: Refsol: %s; Yours: %s"
                                % (
                                    cell.getLocn(),
                                    ("victim" if isVictim else "non-victim"),
                                    ("victim" if pred_isVictim else "non-victim"),
                                )
                            )
                            misclassifications = True
                            cell.victim = pred_isVictim

        print("\nUpdated map, based on classifiers;")
        theMap.display()
        if misclassifications:
            print(
                "Note that misclassifications may affect the agent's optimal performance"
            )
            theMap.victims = victimsList


    def test_p3_s3(self):  # integration
        self.begin_test(3, 3, "integration")

        with open("autograder_files/isVictim_classifier.pk", "rb") as pkf:
            nnData = pickle.load(pkf)
        with open("autograder_files/obstacle_classifier.pk", "rb") as pkf:
            dtData = pickle.load(pkf)

        dt = CF.trainObstacleCost(
            dtData["feature_values"], dtData["classes"], dtData["trainData"]
        )
        nn = CF.trainIsVictim(nnData["trainData"])
        for filename in self.mapNames:
            origMap = readMap.read(filename)
            updatedMap = readMap.read(filename)
            self.update_map(updatedMap, dt, nn, dtData, nnData)
            if len(updatedMap.getVictims()) == 0:
                print("\nYou have misclassified all of the true victims in the map")
                print(
                    "   The search for victims will not work for %s; SKIPPING"
                    % filename
                )
                self.num += len(self.goalTypes)
            else:
                for goalType in self.goalTypes:
                    self.num += 1
                    stu_cost = simulate_search(
                        origMap,
                        updatedMap,
                        ASTAR,
                        goalType,
                        (not args.no_graphics),
                        False,
                    )
                    ref_cost = self.tests[(filename, goalType)]
                    if stu_cost == ref_cost:
                        print("CONGRATS! Your agent found the optimal plan")
                        self.correct += 1
                    elif stu_cost == -1 or stu_cost == None:
                        print("ERROR: Your agent's plan failed")
                    else:
                        print(
                            "WARNING: Your agent's plan was suboptimal: Refsol cost: %d; Yours: %d; Awarding a half point"
                            % (ref_cost, stu_cost)
                        )
                        self.correct += 0.5
        self.end_test()


simSpeed = 0.1  # Speed to run the simulation graphics, in seconds


def simulate_search(origMap, updatedMap, searchType, goalType, useGraphics, debugging):
    print("\n%s search with %s goal" % (searchType, goalType))
    if not searchType in search.SearchTypes:
        raise ValueError("Invalid Search Type")
    searchInstance = search.Search(searchType, Actions, debugging)
    s0 = SAR.createStartState(updatedMap, goalType)
    path, nodeCount, estCost = searchInstance.doSearch(s0)
    if path:
        if searchType in search.USearchTypes:
            print("Node Count: %d, Path (%d): %s" % (nodeCount, len(path), path))
        else:
            print(
                "Node Count: %d, Path (%d): Cost: %d: %s"
                % (nodeCount, len(path), estCost, path)
            )
        simr = simulate.Simulator(
            origMap, goalType, useGraphics, title="S&R: " + searchType, speed=simSpeed
        )
        cost = simr.doPlan(path)
        if cost:
            print("Simulation cost: %s, plan length: %d" % (cost, len(path)))
        else:
            print("PLAN FAILED TO ACHIEVE %s GOALS" % goalType)
        return cost
    else:
        print("%s: Node Count: %d, NO PATH FOUND" % (searchType, nodeCount))
        return - 1


parser = argparse.ArgumentParser()
parser.add_argument("-p", "--problem")
parser.add_argument("-s", "--step")
parser.add_argument("-g", "--goal", nargs="?")
parser.add_argument("-m", "--map", nargs="?")
parser.add_argument("-t", "--test", action="store_true")
parser.add_argument("--no-graphics", action="store_true")
parser.add_argument("--debugging", action="store_true")
parser.add_argument("--generate", action="store_true")
parser.add_argument("--max-steps", nargs="?", default=1000)

args = parser.parse_args()
generating = args.generate

if args.debugging:
    debugging = True
    DT.debugging = True
    NN.debugging = True
    CF.debugging = True

if args.goal and not args.goal in GoalTypes:
    raise Exception(
        "%s unknown goal; options are: %s" % (args.goal, ", ".join(GoalTypes))
    )

if args.test or args.problem == 3 and args.step == 3:
    integrationTest = TestIntegration(
        args.goal, args.map, not args.no_graphics, maxSteps=int(args.max_steps)
    )
    integrationTest.doit(3, 3)
else:
    testHW4 = TestHW4(args.goal, args.map)
    if args.problem == None or args.problem == "1":
        if args.step == None or args.step == "1":
            testHW4.doit(1, 1)
        if args.step == None or args.step == "2":
            testHW4.doit(1, 2)
        if args.step == None or args.step == "3":
            testHW4.doit(1, 3)
    if args.problem == None or args.problem == "2":
        if args.step == None or args.step == "1":
            testHW4.doit(2, 1)
        if args.step == None or args.step == "2":
            testHW4.doit(2, 2)
    if args.problem == None or args.problem == "3":
        if args.step == None or args.step == "1":
            testHW4.doit(3, 1)
        if args.step == None or args.step == "2":
            testHW4.doit(3, 2)

    if not generating:
        print(
            "Total Correct: %d out of %d" % (testHW4.total_correct, testHW4.total_num)
        )
