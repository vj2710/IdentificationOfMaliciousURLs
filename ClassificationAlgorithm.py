import pandas as pd
import statistics as statistics
from sklearn import preprocessing, decomposition
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import KFold
from sklearn.utils import shuffle
import numpy as np
import pickle
import matplotlib.pyplot as plt


# dataset = pd.read_csv('totalresult.txt',header=None)
# dataset = pd.read_csv('datasets/totalresult1.txt',header=None)
# dataset = pd.read_csv('datasets/totalresult2.txt',header=None)
# dataset = pd.read_csv('datasets/totalresult3.txt',header=None)
# dataset = pd.read_csv('datasets/totalresult4.txt',header=None)
# dataset = pd.read_csv('datasets/totalresult5.txt',header=None)

# removing the rows having nan
dataset=dataset.replace(-1, np.nan)
dataset = dataset.dropna(axis=0, how="any")

# shuffling the dataset
dataset = shuffle(dataset)

cols= len(dataset.columns)
rows = len(dataset)
trainingValue=int(0.9*rows)
input=dataset.iloc[0:trainingValue,0:cols-1]
output=dataset.iloc[0:trainingValue,cols-1]
inputVal=dataset.iloc[trainingValue+1:rows,0:cols-1]
outputVal=dataset.iloc[trainingValue+1:rows,cols-1]
test_Accuracy_Logis=list()
test_Accuracy_Percep=list()
test_Accuracy_SGDLog=list()

# scaling
input = pd.DataFrame(preprocessing.scale(input), index = input.index, columns = input.columns)
inputVal = pd.DataFrame(preprocessing.scale(inputVal), index = inputVal.index, columns = inputVal.columns)


coefFile = 'logis.pk'
coefFile_percep='percep.pk'
try:
    with open(coefFile, 'rb') as fi:
        coefficient = pickle.load(fi)
except:
    coefficient=None
try:
    with open(coefFile_percep, 'rb') as fi:
        coefficient_percep = pickle.load(fi)
except:
    coefficient_percep=None


kf = KFold(n_splits=8)

for train_index, test_index in kf.split(input):
    input_train, input_test = input.iloc[train_index, :], input.iloc[test_index, :]
    output_train, output_test = output.iloc[train_index], output.iloc[test_index]
    lgs=LogisticRegression(warm_start=False)
    lgs.fit(input_train,output_train)
    test_Accuracy_Logis.append(lgs.score(input_test, output_test))
    # print("logistic")
    # print(lgs.score(input_test, output_test))
    # print(lgs.score(inputVal, outputVal))

    pct= SGDClassifier(loss='perceptron', eta0=1, learning_rate='constant', penalty=None)
    if coefficient_percep is None:
        pct.fit(input_train, output_train)
    else:
        pct.fit(input_train, output_train,coefficient_percep)
    prediction_val_pct = pct.predict(inputVal)
    test_Accuracy_Percep.append(pct.score(input_test,output_test))
    # print("perceptron")
    # print(pct.score(input_test,output_test))
    # print(pct.score(inputVal,outputVal))

    clf= SGDClassifier(loss='log')
    if coefficient is None:
        clf.fit(input_train, output_train)
        predictionTest =clf.predict(input_test)
    else:
        clf.fit(input_train, output_train,coefficient)
        predictionTest = clf.predict(input_test)
    predictionVal = clf.predict(inputVal)
    test_Accuracy_SGDLog.append(accuracy_score(output_test,predictionTest))
    # print("logisticSGD")
    # print(accuracy_score(output_test, predictionTest))
    # print(clf.score(inputVal,outputVal))

val_Accuracy_Logis=lgs.score(inputVal, outputVal)
val_Accuracy_Percep=pct.score(inputVal,outputVal)
val_Accuracy_SGDLog=clf.score(inputVal,outputVal)
# val_Accuracy_SGDLog=accuracy_score(outputVal,predictionVal)

coefficient=clf.coef_
coefficient_percep=pct.coef_
with open(coefFile, 'wb') as fi:
  pickle.dump(coefficient, fi)
with open(coefFile_percep, 'wb') as fi:
  pickle.dump(coefficient_percep, fi)

# print(test_Accuracy_Logis)
# print(val_Accuracy_Logis)
# print(test_Accuracy_Percep)
# print(val_Accuracy_Percep)
# print(test_Accuracy_Percep)
# print(val_Accuracy_Percep)

mean_test_accuracy_logis = statistics.mean(test_Accuracy_Logis)
mean_test_accuracy_percep = statistics.mean(test_Accuracy_Percep)
mean_test_accuracy_SGDLog=statistics.mean(test_Accuracy_SGDLog)

print("Logistic")
print("Test accuracy")
print(mean_test_accuracy_logis)
print("Validation accuracy")
print(val_Accuracy_Logis)
print("Perceptron")
print("Test accuracy")
print(mean_test_accuracy_percep)
print("Validation accuracy")
print(val_Accuracy_Percep)
print("SGD Logistic")
print("Test accuracy")
print(mean_test_accuracy_SGDLog)
print("Validation accuracy")
print(val_Accuracy_SGDLog)


