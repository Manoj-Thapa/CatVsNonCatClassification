import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import h5py

def load_dataset():
    """

            The dataset is taken from Coursera
            The dataset contains: train_catvnoncat.h5 and test_catvnoncat.h5

           -> a training set of m_train images labeled as cat (y=1) or non-cat (y=0)
           -> a test set of m_test images labeled as cat or non-cat
           -> each image is of shape (num_px, num_px, 3) where 3 is for the 3 channels (RGB).

    """
    
    train_dataset = h5py.File('datasets/train_catvnoncat.h5', "r")
    train_set_x_orig = np.array(train_dataset["train_set_x"][:])  # your train set features
    train_set_y_orig = np.array(train_dataset["train_set_y"][:])  # your train set labels

    test_dataset = h5py.File('datasets/test_catvnoncat.h5', "r")
    test_set_x_orig = np.array(test_dataset["test_set_x"][:])  # your test set features
    test_set_y_orig = np.array(test_dataset["test_set_y"][:])  # your test set labels

    classes = np.array(test_dataset["list_classes"][:])  # the list of classes

    train_set_y_orig = train_set_y_orig.reshape((1, train_set_y_orig.shape[0]))
    test_set_y_orig = test_set_y_orig.reshape((1, test_set_y_orig.shape[0]))

    return train_set_x_orig, train_set_y_orig, test_set_x_orig, test_set_y_orig, classes


def preprocessing():
    """

            Common steps for pre-processing a new dataset are:

            -> Figure out the dimensions and shapes of the problem (m_train, m_test, num_px, …)
            -> Reshape the datasets such that each example is now a vector of size (num_px * num_px * 3, 1)
            -> “Standardise” the data

            Many software bugs in deep learning come from having matrix/vector dimensions that don’t fit.
            If you can keep your matrix/vector dimensions straight you will go a long way toward eliminating
            many bugs.

    """

    # Loading the data (cat/non-cat)
    train_set_x_orig, train_set_y, test_set_x_orig, test_set_y, classes = load_dataset()
    train_set_x_flatten = train_set_x_orig.reshape(train_set_x_orig.shape[0], -1).T
    test_set_x_flatten = test_set_x_orig.reshape(test_set_x_orig.shape[0], -1).T
    train_set_x = train_set_x_flatten / 255
    test_set_x = test_set_x_flatten / 255
    return train_set_x, train_set_y, test_set_x, test_set_y


def initialize_with_zeros(dim):
    """

            This function creates a vector of zeros of shape (dim, 1) for w and initializes b to 0.

            Argument:
            dim -> size of the w vector we want (or number of parameters in this case)

            Returns:
            w -> initialized vector of shape (dim, 1)
            b -> initialized scalar (corresponds to the bias)

    """

    w = np.zeros((dim, 1))
    b = 0

    assert (w.shape == (dim, 1))
    assert (isinstance(b, float) or isinstance(b, int))

    return w, b


def sigmoid(z):
    """

            Compute the sigmoid of z

            Arguments:
            z -> A scalar or numpy array of any size.

            Return:
            s -> sigmoid(z)

    """

    s = 1 / (1 + np.exp(-z))

    return s


def propagate(w, b, X, Y):
    """

            Implement the cost function and its gradient for the propagation explained above

            Arguments:
            w -> weights, a numpy array of size (num_px * num_px * 3, 1)
            b -> bias, a scalar
            X -> data of size (num_px * num_px * 3, number of examples)
            Y -> true "label" vector (containing 0 if non-cat, 1 if cat) of size (1, number of examples)

            Return:
            cost -> negative log-likelihood cost for logistic regression
            dw -> gradient of the loss with respect to w, thus same shape as w
            db -> gradient of the loss with respect to b, thus same shape as b


    """

    m = X.shape[1]

    # FORWARD PROPAGATION (FROM X TO COST)

    A = sigmoid(np.dot(w.T, X) + b)  # compute activation
    cost = -1 / m * (np.sum((np.multiply(Y, np.log(A)) + (np.multiply((1 - Y), np.log(1 - A))))))  # compute cost

    # BACKWARD PROPAGATION (TO FIND GRAD)

    dw = (1 / m) * np.dot(X, (A - Y).T)
    db = (1 / m) * np.sum(A - Y)

    assert (dw.shape == w.shape)
    assert (db.dtype == float)
    cost = np.squeeze(cost)
    assert (cost.shape == ())

    grads = {"dw": dw,
             "db": db}

    return grads, cost


def optimize(w, b, X, Y, num_iterations, learning_rate, print_cost=False):
    """

            This function optimizes w and b by running a gradient descent algorithm

            Arguments:
            w -> weights, a numpy array of size (num_px * num_px * 3, 1)
            b -> bias, a scalar
            X -> data of shape (num_px * num_px * 3, number of examples)
            Y -> true "label" vector (containing 0 if non-cat, 1 if cat), of shape (1, number of examples)
            num_iterations -> number of iterations of the optimization loop
            learning_rate -> learning rate of the gradient descent update rule
            print_cost -> True to print the loss every 100 steps

            Returns:
            params -> dictionary containing the weights w and bias b
            grads -> dictionary containing the gradients of the weights and bias with respect to the cost function
            costs -> list of all the costs computed during the optimization, this will be used to plot the learning curve.

    """

    costs = []  # keep track of cost
    iterations = []  # keep track of iterations

    for i in range(num_iterations):

        # Cost and gradient calculation

        grads, cost = propagate(w, b, X, Y)

        # Retrieve derivatives from grads
        dw = grads["dw"]
        db = grads["db"]

        # update rule

        w = w - learning_rate * dw
        b = b - learning_rate * db

        # Record the costs
        if i % 100 == 0:
            costs.append(cost)
            iterations.append(i)

        # Print the cost every 100 training iterations
        if print_cost and i % 100 == 0:
            print("Cost after iteration %i: %f" % (i, cost))

    params = {"w": w,
              "b": b}

    grads = {"dw": dw,
             "db": db}

    return params, grads, costs, iterations


def predict(w, b, X):
    """

            Predict whether the label is 0 or 1 using learned logistic regression parameters (w, b)

            Arguments:
            w -> weights, a numpy array of size (num_px * num_px * 3, 1)
            b -> bias, a scalar
            X -> data of size (num_px * num_px * 3, number of examples)

            Returns:
            Y_prediction -> a numpy array (vector) containing all predictions (0/1) for the examples in X

    """

    m = X.shape[1]  # Gives the number of training example
    Y_prediction = np.zeros((1, m))  # The number of predication for m training example
    w = w.reshape(X.shape[0], 1)

    # Compute vector "A" predicting the probabilities of a cat being present in the picture

    A = sigmoid(np.dot(w.T, X) + b)

    for i in range(A.shape[1]):  # A.shape[1] is the number of training example

        # Convert probabilities A[0,i] to actual predictions p[0,i]

        if A[0, i] > 0.5:
            Y_prediction[0, i] = 1
        else:
            Y_prediction[0, i] = 0

    assert (Y_prediction.shape == (1, m))

    return Y_prediction


def model(X_train, Y_train, X_test, Y_test, num_iterations=2000, learning_rate=0.5, print_cost=False):
    """

            Builds the logistic regression model by calling the function you've implemented previously

            Arguments:
            X_train -> training set represented by a numpy array of shape (num_px * num_px * 3, m_train)
            Y_train -> training labels represented by a numpy array (vector) of shape (1, m_train)
            X_test -> test set represented by a numpy array of shape (num_px * num_px * 3, m_test)
            Y_test -> test labels represented by a numpy array (vector) of shape (1, m_test)
            num_iterations -> hyperparameter representing the number of iterations to optimize the parameters
            learning_rate -> hyperparameter representing the learning rate used in the update rule of optimize()
            print_cost -> Set to true to print the cost every 100 iterations

            Returns:
            d -> dictionary containing information about the model.

    """

    # initialize parameters with zeros
    w, b = initialize_with_zeros(X_train.shape[0])

    # Gradient descent
    parameters, grads, costs = optimize(w, b, X_train, Y_train, num_iterations, learning_rate, print_cost)

    # Retrieve parameters w and b from dictionary "parameters"
    w = parameters["w"]
    b = parameters["b"]

    # Predict test/train set examples
    Y_prediction_test = predict(w, b, X_test)
    Y_prediction_train = predict(w, b, X_train)

    # Print train/test Errors
    print("\nTrain accuracy: {} %".format(100 - np.mean(np.abs(Y_prediction_train - Y_train)) * 100))
    print("Test accuracy: {} %\n".format(100 - np.mean(np.abs(Y_prediction_test - Y_test)) * 100))

    d = {"costs": costs,
         "Y_prediction_test": Y_prediction_test,
         "Y_prediction_train": Y_prediction_train,
         "w": w,
         "b": b,
         "learning_rate": learning_rate,
         "num_iterations": num_iterations
         }
    
    """
    
            Simple Graph to see the cost after every 100 iterations
 
    """
    
    # plot the cost
    plt.plot(iterations, costs)
    plt.ylabel('Cost')
    plt.xlabel('Iterations (per hundreds)')
    plt.title("Learning rate =" + str(learning_rate))
    plt.show()

    """ 
    
     You can test this algorithm, simply giving your path name of your image 
     
    """

    # Change this to the name of your image file
    my_image = "Dinosaurs.jpeg"

    # Preprocess the image to fit into the algorithm.

    fname = "Images/" + my_image
    image = np.array(Image.open(fname).resize((64, 64)))
    image = image / 255
    final_image = image.reshape(1, 64 * 64 * 3).T
    my_predicted_image = predict(d["w"], d["b"], final_image)

    plt.imshow(image)
    plt.show()

    if my_predicted_image[0][0] == 1:
        print('Your algorithm predicts a "Cat" picture.')
    else:
        print('Your algorithm predicts a "Non-Cat" picture.')

    return d


# Calling preprocessing function to preprocess the data
train_set_x, train_set_y, test_set_x, test_set_y = preprocessing()

# Training the model by calling the model function
d = model(train_set_x, train_set_y, test_set_x, test_set_y, num_iterations=2000, learning_rate=0.01, print_cost=True)
