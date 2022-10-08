# Do not import any additional 3rd party external libraries as they will not
# be available to Gradescope and are not needed
import numpy as np
import pickle
from utils import *
import random
debugging = False  # True


# Return a d0 by d1 array of random numbers, sampled from a Gaussian N(0, 1)
def weight_init_fn(d0, d1):
    np.random.seed(0)
    return np.random.randn(d0, d1)


# Return a 1 by d array of zeroes
def bias_init_fn(d):
    np.random.seed(0)
    return np.zeros((1, d))


class NeuralNet:
    def __init__(self, numLayers=1, numUnits=25, learningRate=1e-3):
        self.create(numLayers, numUnits, learningRate)

    def __repr__(self):
        return "<NN: %d layers, %d inputs, %d outputs>" % (
            self.numLayers,
            self.input_size,
            self.output_size,
        )

    def create(self, numLayers, numUnits, learningRate):
        # TODO: potentially include an activation
        self.numLayers = numLayers + 1
        self.input_size = numUnits
        self.hidden_size = numUnits // 2
        self.output_size = 2  # Binary Classification Problem
        self.activations = [Sigmoid() for i in range(self.numLayers)]
        self.criterion = SoftmaxCrossEntropy()  # Determine this
        self.lr = learningRate

        # The first set of weights are connections from all inputs to the first hidden layer
        self.weights = [weight_init_fn(self.input_size, self.hidden_size)]
        # add the intermediate layers
        # The next sets of weights are connections to the next hidden layers
        for i in range(numLayers - 1):
            self.weights.append(weight_init_fn(self.hidden_size, self.hidden_size))
        # The final set of weights connects the last hidden layer and the output (classification) layer
        self.weights.append(weight_init_fn(self.hidden_size, self.output_size))

        # Set bias weights from to each hidden layer and to the ouput layer
        self.bias = []
        for i in range(numLayers):
            self.bias.append(bias_init_fn(self.hidden_size))
        self.bias.append(bias_init_fn(self.output_size))

        # ___________________________________________
        # Don't change this
        self.dW = [np.zeros_like(layer) for layer in self.weights]
        self.db = [np.zeros_like(layer) for layer in self.bias]

        self.input = None
        self.ins = None
        self.outs = None  # this array is useful for activations

    def zero_grads(self):
        self.dW = [np.zeros_like(self.dW[i]) for i in range(self.numLayers)]
        self.db = [np.zeros_like(self.db[i]) for i in range(self.numLayers)]
        return

    def step(self):
        for i in range(self.numLayers):
            self.weights[i] = self.weights[i] - self.lr * self.dW[i]
            self.bias[i] = self.bias[i] - self.lr * self.db[i]
        return

    # Compute the feed-forward calculation of the neural networks
    # "input" is a numpy array of shape (self.input_size, )
    def feed_forward(self, input):
        input = np.expand_dims(input, axis=0)
        self.input = input
        self.ins = []  # Inputs to the ith layer
        self.outs = []  # Outputs of the ith layer
        outs = input
        for i in range(self.numLayers):
            # Compute "ins" - the inputs to the ith layer
            ins = np.zeros(self.bias[i].shape)
            # BEGIN STUDENT CODE FOR PROBLEM 2, STEP 1

            ins = np.dot(outs, self.weights[i]) + self.bias[i]
            # for j in range(len(ins)):
            #     for k in range(len(self.weights[i])):
            #         print(outs[k])
            #         ins[0][j] += outs[0][k]*self.weights[i][k][j]
            #     ins[j] += self.bias[i][j]
            # END STUDENT CODE FOR PROBLEM 2, STEP 1

            # Save intermediate results; do not delete this
            self.ins.append(ins)

            # Compute "outs" - activating the nodes in the ith layer, based on the "ins"
            outs = np.zeros(self.bias[i].shape)

            # BEGIN STUDENT CODE FOR PROBLEM 2, STEP 1
            #print(self.activations)
            # print(ins)
            # print(outs)
            # print(self.activations)
            for j in range(len(ins)):
                outs[j] = self.activations[i](ins[j])
                #outs[0][j] = x(ins[j])
                            # END STUDENT CODE FOR PROBLEM 2, STEP 1
            self.outs.append(outs)

            ins = outs

        return self.ins[-1]  # Return this b/c the output layer is not activated

    def back_prop(self, labels):
        inp = self.input
        inputs = [inp] + self.outs[:-1]
        for i in range(self.numLayers):
            j = self.numLayers - i - 1
            inp = inputs[j]
            if i == 0:
                loss = self.criterion(self.ins[-1], labels)
                dLoss_dy = self.criterion.derivative()
                dLoss_dz = dLoss_dy
            else:
                dLoss_dy = np.dot(dLoss_dz, np.transpose(self.weights[j + 1]))
                dy_dz = self.activations[j].derivative()
                dLoss_dz = dLoss_dy * dy_dz

            self.dW[j] = np.dot(np.transpose(inp), dLoss_dz)
            self.db[j] = np.sum(dLoss_dz, axis=0)

        return loss

    # input is an array of feature values
    # returns the output that has the highest weight
    def classify(self, input):
        pred = self.feed_forward(input)
        # print(pred[0], pred.shape, input.shape, input[0])
        label = np.argmax(pred[0], axis=0)

        return label

    # trainingSet : a list of tuples (label, input), where label is
    #               one of the class values (0 or 1), and input is
    #               an array of feature values
    # Trains the network for 1 epoch and returns the training error
    def train(self, trainingSet):
        n = len(trainingSet)
        train_loss = 0.0
        train_error = 0.0
        for i in range(len(trainingSet)):
            label, data = trainingSet[i]

            self.zero_grads()
            pred = self.feed_forward(data)
            label_array = np.array([[1, 0] if (label == 0) else [0, 1]])
            loss = self.back_prop(label_array)
            train_loss += np.sum(loss)
            predicted_label = np.argmax(pred[0], axis=0)
            if label != predicted_label:
                train_error += 1
            self.step()

        if debugging:
            print(
                "Training Error: %.3f; Training Loss: %.3f"
                % (train_error / n, train_loss / n)
            )

        return train_error / n


# Train a neural net classifer
# dataset is a list of (label, nparray) tuples, the nparray is the input vector
#    whose size should be the number of inputs to the neural network
# numLayers is the number of layers (= hidden layers + output layer)
# numEpochs is the number of epochs to train the network
# learningRate is how much effect back_prop has
# Return the network that you think will perform best on unseen test data
#   that is, has good performance, but doesn't overfit the data


def trainNetwork(dataset, numLayers=1, numEpochs=50, learningRate=1e-3, nfold=5):
    # Initialize a neural network class with the appropriate parameters
    # For each epoch, train the network and validate it.
    # You might want to print out the train and validation errors for each epoch
    #   to see how they are converging (note that the "train" function returns
    #   error but the "validate" function returns accuracy, which is 1-error).
    # Use N-fold cross-validation to avoid overfitting (default is 5-fold);
    #   that is, split the training data into N chunks and use N-1 to train
    #   and 1 to test, N times each (use separate networks for each, to avoid
    #   retraining the same network)

    bestNetwork = None
    bestAcc = 0
    numInputs = dataset[0][1].shape[0]


    # BEGIN STUDENT CODE FOR PROBLEM 2, STEP 2
    chunkSize = len(dataset) // nfold
    chunks = []

    #splits data into nfold chunks
    for N in range(nfold):
        chunks.append(dataset[N*chunkSize:(N+1)*chunkSize])

    for N in range(nfold):
        #print("Nfold ", N)
        test = chunks[N] #choose one chuck to train on
        nn = NeuralNet(numLayers,numInputs,learningRate);
        for i in range(numEpochs):
            for chunk in chunks:
                if chunk is not test: #all other chunks are training
                    nn.train(chunk)
        acc = validateNN(nn, test)
        if acc > bestAcc:
            bestAcc = acc
            bestNetwork = nn
    # END STUDENT CODE FOR PROBLEM 2, STEP 2
    return bestNetwork
