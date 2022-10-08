#
# Create a decision tree using information gain to split the nodes
#

import re
import math
import itertools
from utils import compareTrees

debugging = False  # True


# p(class)
def prob(classs, dataset):
    classCount = sum(datum[0] == classs for datum in dataset)
    return classCount / len(dataset)


# p(feature_value)
def fprob(feature, feature_value, features, dataset):
    feature_idx = features.index(feature)
    featureCount = sum(datum[1][feature_idx] == feature_value for datum in dataset)
    return featureCount / len(dataset)


# p(feature_value|feature)
def condProb(classs, feature, feature_value, features, dataset):
    feature_idx = features.index(feature)
    featureCount = sum(datum[1][feature_idx] == feature_value for datum in dataset)
    if featureCount == 0:
        return 0
    classCount = sum(
        datum[0] == classs and datum[1][feature_idx] == feature_value
        for datum in dataset
    )
    return classCount / featureCount


def entropy(probs):
    return -sum(prob * (0 if prob == 0 else math.log2(prob)) for prob in probs)


class Node:
    def __init__(self):
        self.children = []
        self.feature = None
        self.children = []
        self.classs = None

    def getChildren(self):
        return self.children

    def isLeaf(self):
        return self.getClass() is not None

    def getClass(self):
        return self.classs

    def setClass(self, classs):
        self.classs = classs

    def getFeature(self):
        return self.feature

    def __repr__(self):
        if self.getFeature():
            return "<DT Node %s: %d children>" % (
                self.getFeature(),
                len(self.getChildren()),
            )
        elif self.getClass():
            return "<DT Leaf: %s>" % self.getClass()
        else:
            return "<DT Node>"


class DecisionTree:
    # "feature_values" is a list of pairs, each pair is a feature name and
    #   a list of values that feature can take
    #   For instance [('color', ['red', 'yellow', 'green']), ('shape', [square, round])]
    # "classes" is a list of values that the decision tree can output
    # "dataset" is a list whose first value is the class and the remaining values are the
    #   feature values (where the order of features matches that of feature_values)
    def __init__(self, feature_values, classes):
        self.features = [fv[0] for fv in feature_values]
        self.values = {}
        for fv in feature_values:
            self.values[fv[0]] = fv[1]
        self.classses = classes
        self.root = None

    def getRoot(self):
        return self.root

    def getClasses(self):
        return self.classses

    def getFeatures(self):
        return self.features

    def getFeatureValues(self, feature):
        return self.values[feature]

    def createNode(self, feature):
        if feature not in self.getFeatures():
            # self.display()
            raise Exception(
                "'%s' is not a valid feature: %s" % (feature, self.getFeatures())
            )
        node = Node()
        node.feature = feature
        if not self.root:
            self.root = node  # The first node created is the root node
        return node

    def createLeaf(self, classs):
        if classs not in self.getClasses():
            raise Exception(
                "'%s' is not a valid class: %s" % (classs, self.getClasses())
            )
        node = Node()
        node.setClass(classs)
        return node

    def addChild(self, parent, feature_value, child):
        if parent.isLeaf():
            raise Exception("%s is not an interior node" % parent)
        if feature_value not in self.values[parent.getFeature()]:
            raise Exception(
                "'%s' is not a valid value for feature %s: %s"
                % (feature_value, parent.getFeature(), self.values[parent.getFeature()])
            )
        if debugging:
            print("addChild", parent, feature_value, child)
        parent.getChildren().append((feature_value, child))

    def mode(self, dataset):
        classes = self.getClasses()
        classCounts = [0] * len(classes)
        for datum in dataset:
            cindex = classes.index(datum[0])
            classCounts[cindex] += 1
        return classes[classCounts.index(max(classCounts))]

    # If all the class values in the dataset are the same, return that value, o/w return None
    def uniformClass(self, dataset):
        classs = dataset[0][0]
        for datum in dataset[1:]:
            if datum[0] != classs:
                return None
        return classs

    # Compare function for choosing features
    # feature_1, feature_2: feature name of two features
    # feature_value_1, feature_value_2: the info gain of the two features
    # Return True iff the first feature is better than the second feature
    def featureGreaterHandlingTies(
        self, feature_1, feature_value_1, feature_2, feature_value_2
    ):
        if feature_value_1 > feature_value_2:
            return True
        elif feature_value_2 > feature_value_1:
            return False
        else:
            # feature_1 lexicographically precedes feature_2
            if (feature_1 == None):
                return False
            elif (feature_2 == None) or (feature_1.lower() < feature_2.lower()):
                return True
            else:
                return False

    # Return the subset of dataset that has the given value of the feature
    def subDataset(self, feature, feature_value, dataset):
        if feature_value not in self.getFeatureValues(feature):
            raise Exception(
                "'%s' is not a valid value for feature '%s'" % (feature_value, feature)
            )
        findex = self.getFeatures().index(feature)
        sub_data = [datum for datum in dataset if (datum[1][findex] == feature_value)]
        return sub_data

    def infoGain(self, feature, dataset):
        if len(dataset) == 0:
            return 0

        # What could you use to find the entropy?
        H_class = entropy([prob(c,dataset) for c in self.getClasses()])
        # How do you find the conditional probability?
        E_H_cond_class = 0
        for fVal in self.getFeatureValues(feature):
            fp = fprob(feature, fVal, self.getFeatures(), dataset)
            cp = entropy([condProb(c,feature,fVal,self.getFeatures(),dataset) for c in self.getClasses()])
            E_H_cond_class += fp*cp
        # How do you get information gain from the two components above?
        # BEGIN STUDENT CODE FOR PROBLEM 1, STEP 1
        # END STUDENT CODE FOR PROBLEM 1, STEP 1
        return H_class - E_H_cond_class

    # Return a sub-decision tree based on the given features and data
    # "dataset" is a list whose first value is the class and the remaining values are the
    #   feature values (where the order of features matches that of feature_values)
    #
    # Return a sub-decision tree based on the given features and data
    def createTree(self, dataset, features=None):
        if features is None:
            features = self.getFeatures()
        #  What should be returned if the dataset is all in one class?
        if self.uniformClass(dataset):
            if debugging:
                print("Uniform leaf:")
            # BEGIN STUDENT CODE FOR PROBLEM 1, STEP 2
            # END STUDENT CODE FOR PROBLEM 1, STEP 2
            return self.createLeaf(self.mode(dataset))
        #  What about if there are no more features left to split on?
        elif len(features) == 0:
            if debugging:
                print("No more features:")
            # BEGIN STUDENT CODE HERE FOR PROBLEM 1, STEP 2
            return self.createLeaf(self.mode(dataset))
            # END STUDENT CODE HERE FOR PROBLEM 1, STEP 2
        else:
            # Use infoGain to pick a feature F and create a node R for it.
            # Then, split the dataset based on that feature and generate
            #   the appropriate subtrees.
            # return the subtree rooted at R

            if debugging:
                print("Using info gain to split on %s" % features)
            # BEGIN STUDENT CODE FOR PROBLEM 1, STEP 2
            bestFeature = features[0]
            for feature in features:
                if self.featureGreaterHandlingTies(feature, self.infoGain(feature,dataset),bestFeature,self.infoGain(bestFeature,dataset)):
                    bestFeature = feature;
            node = self.createNode(bestFeature)
            for fVal in self.getFeatureValues(bestFeature):
                subDS = self.subDataset(bestFeature,fVal,dataset)

                if (len(subDS) == 0):
                    self.addChild(node,fVal,self.createLeaf(self.mode(dataset)))
                else:
                    self.addChild(node,fVal,self.createTree(subDS,[f for f in self.getFeatures() if f != bestFeature]))
            return node
            # END STUDENT CODE FOR PROBLEM 1, STEP 2

    def classify(self, feature_values, node=None):
        if not node:
            node = self.getRoot()
            # Empty tree - Hasn't been trained, yet
            if not node:
                return -1
        if node.isLeaf():
            return node.getClass()
        else:
            feature = node.getFeature()
            children = node.getChildren()
            findex = self.getFeatures().index(feature)
            feature_value = feature_values[findex]
            for child in children:
                if child[0] == feature_value:
                    return self.classify(feature_values, child[1])
            raise Exception("Unable to classify feature '%s'" % node.getFeature())

    # Prune to a maximum depth, starting at the given treeNode
    # For a non-leaf node that has all its children pruned, set its "value"
    #  to the class that is the mode of the sub-dataset for that node
    def prune(self, dataset, depth, treeNode=None):

        if not treeNode:
            treeNode = self.getRoot()
        # BEGIN STUDENT CODE FOR PROBLEM 1, STEP 3
        if(depth == 1 and not treeNode.isLeaf()):
            treeNode.setClass(self.mode(dataset))
        elif(depth != 1):
            for child in treeNode.getChildren():
                #print(child[1].getFeature(),child[1].getClass())
                #self.prune(dataset,depth-1,child[1])
                self.prune(self.subDataset(treeNode.getFeature(),child[0],dataset),depth-1,child[1])

        # END STUDENT CODE FOR PROBLEM 1, STEP 3
        pass


    def display(self, indent=0):
        if self.getRoot() is None:
            self.indent_print("No tree", indent)
        else:
            self.display_sub(self.getRoot(), indent)

    def indent_print(self, string, indent):
        print("%s%s" % ("                                        "[:indent], string))

    def display_sub(self, node, indent, fv="Root"):
        if node.getClass():
            self.indent_print("%s: class: %s" % (fv, node.getClass()), indent)
        else:
            self.indent_print("%s: split: %s:" % (fv, node.getFeature()), indent)
            indent += 2
            for child in node.getChildren():
                self.display_sub(child[1], indent, child[0])


def readDataset(filename):
    dataset, features, classes = [], [], []
    with open(filename) as f:
        lines = f.readlines()
        for line in lines:
            # remove cr
            line = line[:-1]
            if len(line) > 0 and line[0] != "#":
                words = re.sub(r"[:,\n]", " ", line).split()
                if words[0] == "features":
                    features = [(feature, []) for feature in words[1:]]
                else:  # Add data
                    classs = words[0]
                    feature_values = [
                        int(w)
                        if re.match(r"^-?\d+?$", w)
                        else float(w)
                        if re.match(r"^-?\d+(?:\.\d+)?$", w)
                        else w
                        for w in words[1:]
                    ]
                    dataset.append((classs, feature_values))
                    # Add feature values to features
                    for idx in range(len(features)):
                        if not feature_values[idx] in features[idx][1]:
                            features[idx][1].append(feature_values[idx])
                    if classs not in classes:
                        classes.append(classs)

        # Sort the various lists
        for feature in features:
            feature[1].sort()
        classes.sort()
        return dataset, features, classes
