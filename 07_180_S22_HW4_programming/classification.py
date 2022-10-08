import neuralNet as NN
import decisionTree as DT

# Use a neural network to classify an image as a victim or not.
# image: a flattened array of a 5 * 5 image
# network: a pretrained neural network
# return a boolean indicating whether the image contains a victim or not
def isVictim(image, network):
    return network.classify(image)

# Use a decision tree to classify an obstacle's cost
# features: a list of feature values (in the same order as the decision tree's features)
# decisionTree: a pretrained decision tree
def obstacleCost (features, decisionTree):
    return decisionTree.classify(decisionTree, features)

# Train the decision tree for classifying the obstruction cost of a cell
# feature_values: a list of (feature, list of values) that describe the possible features
# classes: a list of the possible obstruction costs (1, 2, 3, 4)
# trainingSet: a list of (label, fvalues), where the label is the cost of the cell and
#              fvalues are the values of the features for that training datum (in the
#              same order as feature_values
# return a decision tree that you feel will work best on unseen test data.
#    Feel free to use cross-validation and pruning to produce the best classifier that you can
def trainObstacleCost (feature_values, classes, trainingSet):
    dt = DT.DecisionTree(feature_values, classes)
    # BEGIN STUDENT CODE FOR PROBLEM 3
    #dt.createNode(dt.createTree(dataset))
    dt.root = dt.createTree(trainingSet);
    dt.prune(trainingSet,4)
    # END STUDENT CODE FOR PROBLEM 3
    return dt

# Train the neural network for classifying whether an image is a victim
# trainingSet: a list of (label, image), where the label is either
#              1 (victim) or 0 (non-victim)
# return a neural network that you feel will work best on unseen test data.
#    Feel free to use different parameters (number of layers, epochs, learning rate)
#    and cross-validation to produce the best classifier that you can
def trainIsVictim (trainingSet):
    # BEGIN STUDENT CODE FOR PROBLEM 3
    # END STUDENT CODE FOR PROBLEM 3
    return NN.trainNetwork(trainingSet,numLayers=2,numEpochs=500,learningRate=1e-3,nfold=5);
