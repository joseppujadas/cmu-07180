import numpy as np


def compareTrees(tree1, tree2, debugging=False):
    result = compareTrees1(tree1.getRoot(), tree2.getRoot(), debugging)
    if result and debugging:
        print("The trees are the same")
    return result


def compareTrees1(nodeTree1, nodeTree2, debugging=False):
    if not nodeTree1 or not nodeTree2 or (nodeTree1.isLeaf() != nodeTree2.isLeaf()):
        if debugging:
            print("trees have different shape")
        return False
    elif nodeTree1.isLeaf():
        if nodeTree1.getClass() != nodeTree2.getClass():
            if debugging:
                print(
                    "trees have different classes: %s vs %s"
                    % (nodeTree1.getClass(), nodeTree2.getClass())
                )
            return False
        else:
            return True
    elif nodeTree1.getFeature() != nodeTree2.getFeature():
        if debugging:
            print(
                "trees have different features at same branch; %s vs %s"
                % (nodeTree1.getFeature(), nodeTree2.getFeature())
            )
        return False
    elif len(nodeTree1.getChildren()) != len(nodeTree2.getChildren()):
        if debugging:
            print("trees have different shape")
        return False
    else:
        for value, child in nodeTree1.getChildren():
            child2 = [c for v, c in nodeTree2.getChildren() if v == value][0]
            if not compareTrees1(child, child2, debugging):
                return False
        return True


def validateDT(DT, testData, pclass=None, debugging=False):
    correct = tp = tn = fp = fn = 0
    for classs, values in testData:
        answer = DT.classify(values)
        if answer == classs:
            correct += 1
            if pclass is not None and answer == pclass:
                tp += 1
            else:
                tn += 1
        else:
            if debugging:
                print(
                    "    misclassified %s as class '%s'; expected '%s'"
                    % (values, answer, classs)
                )
            if pclass is not None and answer == pclass:
                fp += 1
            else:
                fn += 1
    accuracy = correct / len(testData)
    if debugging:
        if pclass is not None:
            print("  TP: %s; TN: %s; FP: %s; FN: %s" % (tp, tn, fp, fn))
            precision = tp / (tp + fp)
            recall = tp / (tp + fn)
            print(
                "  Accuracy: %.1f%%; Precision: %.1f%%; Recall: %.1f%%"
                % (100 * accuracy, 100 * precision, 100 * recall)
            )
        else:
            print("  Accuracy: %.1f%%" % (100 * accuracy))
    return accuracy


# testingSet : a list of tuples (label, input), where label is
#              one of the class values (0 or 1), and input is
#              an array of feature values
# calculates the precision, recall, and accuracy of the network,
#   and returns the accuracy
def validateNN(NN, testingSet, pclass=1, debugging=False):
    tp = tn = fp = fn = 0

    for label, data in testingSet:
        result = NN.classify(data)

        if label == result:
            if label == pclass:
                tp += 1
            else:
                tn += 1
        else:
            if debugging:
                print(
                    "    misclassified %s as class '%s'; expected '%s'"
                    % (data, result, label)
                )
            if result == pclass:
                fp += 1
            else:
                fn += 1

    precision = tp / max(tp + fp, 1)
    recall = tp / max(tp + fn, 1)
    accuracy = (tp + tn) / (tp + fp + fn + tn)
    if debugging:
        print("  TP: %s; TN: %s; FP: %s; FN: %s" % (tp, tn, fp, fn))
        print(
            "  Accuracy: %.1f%%; Precision: %.1f%%; Recall: %.1f%%"
            % (100 * accuracy, 100 * precision, 100 * recall)
        )

    return accuracy


class Criterion(object):

    """
    Interface for loss functions.
    """

    # Nothing needs done to this class, it's used by the following Criterion classes

    def __init__(self):
        self.logits = None
        self.labels = None
        self.loss = None

    def __call__(self, x, y):
        return self.forward(x, y)

    def forward(self, x, y):
        raise NotImplementedError

    def derivative(self):
        raise NotImplementedError


class SoftmaxCrossEntropy(Criterion):

    """
    Softmax loss
    """

    def __init__(self):

        super(SoftmaxCrossEntropy, self).__init__()
        self.sm = None

    def forward(self, x, y):
        self.logits = x
        self.labels = y
        a = np.amax(x, axis=1)
        self.sm = np.exp(x) / ((np.sum(np.exp(x), axis=1) + 1e-8)[:, None])
        return -np.sum(x * y, axis=1) + (
            a + np.log(np.sum(np.exp(x - a[:, None]), axis=1))
        )

    def derivative(self):
        return -self.labels + self.sm


class Activation(object):

    """
    Interface for activation functions (non-linearities).

    In all implementations, the state attribute must contain the result, i.e. the output of forward (it will be tested).
    """

    # No additional work is needed for this class, as it acts like an abstract base class for the others

    def __init__(self):
        self.state = None

    def __call__(self, x):
        return self.forward(x)

    def forward(self, x):
        raise NotImplementedError

    def derivative(self):
        raise NotImplementedError


class ReLU(Activation):

    """
    ReLU non-linearity
    """

    def __init__(self):
        super(ReLU, self).__init__()

    def forward(self, x):
        self.x = np.array(x)
        self.state = (x > 0) * x
        return self.state

    def derivative(self):
        return ((self.x > 0) * 1).astype(np.float64)


class Sigmoid(Activation):

    """
    Sigmoid non-linearity
    """

    # Remember do not change the function signatures as those are needed to stay the same for AL

    def __init__(self):
        super(Sigmoid, self).__init__()

    def forward(self, x):
        x = np.array(x)
        self.state = 1 / (1 + np.exp(-x))
        return self.state

    def derivative(self):
        return self.state * (1 - self.state)
