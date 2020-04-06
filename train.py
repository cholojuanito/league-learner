import csv
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
import matplotlib.pyplot as plt


def train(input):
    pass


def shuffle_data(X, y):
    """ Shuffle the data! This _ prefix suggests that this method should only be called internally.
        It might be easier to concatenate X & y and shuffle a single 2D array, rather than
            shuffling X and y exactly the same way, independently.
    """
    new_idxs = np.random.permutation(X.shape[0])
    X = X[new_idxs]
    y = y[new_idxs]

    return (X, y)


def split_data(datapts, labels, split_percent=0.7):
    """ 
    Splits the data points and labels in the data set according to the split_amt 
    which is a number from 0.0 to 1.0 representing a percentage

    Returns:
        tuple, (train_set, train_labels, test_set, test_labels)

    """
    num_datapts = datapts.shape[0]
    train_set = datapts[: int((num_datapts + 1) * split_percent)]
    train_labels = labels[: int((num_datapts + 1) * split_percent)]
    test_set = datapts[int(num_datapts * split_percent + 1) :]
    test_labels = labels[int(num_datapts * split_percent + 1) :]

    return (train_set, train_labels, test_set, test_labels)


def initialize_training_data(data_file, split, shuffle):
    data = []
    with open(data_file) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")
        line_count = 0
        for row in csv_reader:
            if line_count != 0:
                data_pt = [float(x) for x in row]
                data.append(data_pt)
            line_count += 1
        num_rows = len(data)

    data = np.asarray(data)

    if shuffle:
        data, labels = shuffle_data(data[:, :-1], data[:, -1])
    else:
        labels = data[:, -1]
        data = data[:, :-1]

    train_inputs, train_targets, val_inputs, val_targets = split_data(
        data, labels, split_percent=split
    )

    return (
        np.asarray(train_inputs),
        np.asarray(train_targets),
        np.asarray(val_inputs),
        np.asarray(val_targets),
    )


if __name__ == "__main__":
    filename = "data/chal.csv"
    split = 0.7
    shuffle = True
    train_inputs, train_targets, test_inputs, test_targets = initialize_training_data(
        filename, split, shuffle
    )

    log = LogisticRegression(random_state=0, solver="lbfgs", multi_class="ovr")
    bayes = GaussianNB()

    log.fit(train_inputs, train_targets)
    log_score = log.score(test_inputs, test_targets)

    # plt.figure(1, figsize=(4, 3))
    # plt.clf()
    # plt.scatter(train_inputs[:, 15], train_targets, color="black", zorder=20)
    # plt.show()

    bayes.fit(train_inputs, train_targets)
    bay_score = bayes.score(test_inputs, test_targets)
    test_probs = bayes.predict_proba(test_inputs)
    test_log_probs = bayes.predict_log_proba(test_inputs)

    print("Log Regress Info")
    print(log_score)
    print(log.class_weight)
    print(log.intercept_)
    print(log.coef_)

    # print("\n\nBayes Info")
    # print(bay_score)
    # print(bayes.classes_)
    # print(bayes.class_count_)
    # print(f"Probabilities: {test_probs}")
    # print(f"Log probs: {test_log_probs}")
