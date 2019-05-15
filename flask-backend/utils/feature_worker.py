import numpy as np
import matplotlib.pyplot as plt
import csv
import string
import random
import re
import json
import operator
from copy import copy
from nltk.corpus import stopwords
from nltk.tokenize import TweetTokenizer
from nltk.stem import PorterStemmer
class FeatureWorker(object):
    def get_tweets(self):
        csvname = './onepersontweets.csv'
        tweets = open(csvname, 'r')
        csvreader = csv.reader(tweets)

        data = []
        for row in csvreader:
            if row[0] == "Tweets":
                pass
            else:
                x = row[0].lower()
                data.append(x)
        return (data)


    def compute_model(self,tweet, b, weights):
        '''
        computes linear combination of input points,
        ignores words that haven't been seen in training set
        input:
            tweet - str, tweet from a row of data
            b - float, bias
            weights - dict, dictionary of word, weight pairs
        output:
            model - float, linear combination of WX + b
        '''
        wx = 0
        for word in tweet:
            if word not in weights:
                # ignores words that haven't been seen in training set
                continue
            wx += weights[word]
        model = b + wx
        return model


    def get_category(self,tweets):
        weights = dict()
        for i in range(102, 115):
            with open('./data/' + str(i) + '.json') as file:
                weights[i] = json.load(file)
        scores = []
        for i in range(11):
            scores.append(0)
            for tweet in tweets:
                scores[i] += self.compute_model(tweet, -1, weights[i + 102])
        return (np.argmax(scores) + 102)


    def calculate(self,tweets, weights):
        final = []
        for i in weights.keys():
            track = 0
            for j in tweets:
                track += self.compute_model(j, -1, weights[i])
            final.append(track)
        return (final)


    # read in csv file
    # csvname = datapath + 'training.1600000.processed.noemoticon.csv'
    # datapath = './'
    def create_model(self,class_num):
        csvname = './refinedtweets.csv'
        data = open(csvname, "r", encoding="utf-8")
        csvReader = csv.reader(data)

        all_data = []

        for row in csvReader:
            try:
                y = int(row[1])
                if y == class_num:
                    y = 1
                else:
                    y = 0
            except:
                pass
            # lowercase tweet
            x = row[0].lower()
            # extract columns of interest (tweet, sentiment)
            # negative and positive indicators converted to 0 and 1
            all_data.append((x, y))

        # used to tokenize and remove stop words
        tknzr = TweetTokenizer(strip_handles=True, reduce_len=True)
        stop_words = set(stopwords.words('english'))
        # used to remove digits
        remove_digits = str.maketrans('', '', string.digits)
        # used to stem
        stemmer = PorterStemmer()

        for n, instance in enumerate(all_data):
            tweet = instance[0]
            sentiment = instance[1]
            # remove 'RT'
            tweet = re.sub(r"RT", "", tweet)
            tweet = re.sub(r"rt", "", tweet)
            # using regular expressions, remove URLs from tweet
            tweet = re.sub(r"http://\S+", "", tweet)
            tweet = re.sub(r"https://\S+", "", tweet)
            tweet = re.sub(r"www.\S+", "", tweet)
            tweet = re.sub(r"\S+.com[/\S+]*", "", tweet)
            tweet = re.sub(r"\S+.org[/\S+]*", "", tweet)
            tweet = re.sub(r"\S+.net[/\S+]*", "", tweet)
            # regular expression to remove emails
            tweet = re.sub(r"\S*@\S*\s?", "", tweet)
            tokens = tknzr.tokenize(tweet)
            # remove punctuation from ends of each token as well as numerical digits
            for i, token in enumerate(tokens):
                tokens[i] = token.strip(string.punctuation).translate(remove_digits)
            # remove stop words and empty strings
            tokenized_tweet = [word for word in tokens if (word not in stop_words and word != '')]
            # stemming
            tokenized_tweet = [stemmer.stem(token) for token in tokenized_tweet]
            # tuples are used so that each instance is immutable
            all_data[n] = (tokenized_tweet, sentiment)

        num_examples = len(all_data)
        print("total number of examples: ", num_examples)
        pos_data = []
        neg_data = []
        # split positive and negative data into separate lists
        for instance in all_data:
            if instance[1] == 1:
                pos_data.append(instance)
            else:
                neg_data.append(instance)
        num_pos = len(pos_data)
        num_neg = len(neg_data)
        print("total number of postive examples: ", num_pos)
        print("total number of negative examples: ", num_neg, "\n")

        # shuffle all data randomly
        random.shuffle(pos_data)
        random.shuffle(neg_data)
        # 60% training set
        training_set = pos_data[:int(num_pos * .6)] + neg_data[:int(num_neg * .6)]
        # 10% validataion set
        validation_set = pos_data[int(num_pos * .6):int(num_pos * .7)] + neg_data[int(num_neg * .6):int(num_neg * .7)]
        # 30% test set
        test_set = pos_data[int(num_pos * .7):] + neg_data[int(num_neg * .7):]

        # verifying 60-30-10 split and randomization
        print("training set length: ", len(training_set))
        print(training_set[0], "\n")
        print("validation set length: ", len(validation_set))
        print(validation_set[0], "\n")
        print("testing set length: ", len(test_set))
        print(test_set[0], "\n")

        # dictionary of all words present in training data with corresponding weight
        words = {}
        for instance in training_set:
            for word in instance[0]:
                # make unique
                if word not in words:
                    # initialization of weight as 0
                    words[word] = 0

        def model(tweet, b, weights):
            '''
            computes linear combination of input points,
            ignores words that haven't been seen in training set
            input:
                tweet - str, tweet from a row of data
                b - float, bias
                weights - dict, dictionary of word, weight pairs
            output:
                model - float, linear combination of WX + b
            '''
            wx = 0
            for word in tweet:
                if word not in weights:
                    # ignores words that haven't been seen in training set
                    continue
                wx += weights[word]
            model = b + wx
            return model

        def ridge_norm(weights):
            '''
            computes squared L2 norm of weights vector
            input:
                weights - dict, dictionary of word, weight pairs
            output:
                norm - float, squared L2 norm of weights vector
            '''
            arr = np.array(list(weights.values()))
            norm = (np.linalg.norm(arr)) ** 2
            return norm

        def pos_cost(tweet, reg, b, weights):
            '''
            computes cost for a positive example
            input:
                tweet - str, tweet from a row of data
                reg - float, ridge penalty value
                b - float, bias
                weights - dict, dictionary of word, weight pairs
            output:
                cost - float, cost for a positive example
            '''
            cost = -np.log(1 / (1 + np.exp(-model(tweet, b, weights)))) + (reg / 2) * (ridge_norm(weights))
            return cost

        def neg_cost(tweet, reg, b, weights):
            '''
            computes cost for a negative example
            input:
                tweet - str, tweet from a row of data
                reg - float, ridge penalty value
                b - float, bias
                weights - dict, dictionary of word, weight pairs
            output:
                cost - float, cost for a negative example
            '''
            cost = -np.log(1 - 1 / (1 + np.exp(-model(tweet, b, weights)))) + (reg / 2) * (ridge_norm(weights))
            return cost

        def plot_cost_histories(cost_history):
            '''
            plots cost function history plot
            input:
                cost_history - list, list of costs at every 10% of dataset gone through
            output:
                None
            '''
            num_its = len(cost_history)
            iterations = np.linspace(1, num_its, num_its)
            plt.plot(iterations, cost_history)
            plt.title("Cost Function History Plot")
            plt.xlabel("iterations (every 10% of dataset)")
            plt.ylabel("cost")

        # gradient descent function
        def gradient_descent(gamma, max_eps, reg, b, w0, beta):
            '''
            performs binary (ridge) logistic regression with gradient descent
            input:
                gamma - float, learning rate
                max_eps - int, maximum number of epochs
                reg - float, ridge penalty value
                b - float, bias
                w0 - dict, dictionary of word, weight pairs for initial weights
            output:
                new_weights - dict, dictionary of word, weight pairs for final weights
            '''
            # copy initial weights
            new_weights = copy(w0)
            z = np.zeros((np.shape(w0)))  # momentum term

            for k in range(max_eps):
                # randomly shuffle data at beginning of each epoch
                random.shuffle(training_set)
                tweet_counter = 0
                for instance in training_set:
                    # remove duplicate words in tweet
                    tweet = list(set(instance[0]))
                    sentiment = instance[1]
                    p = 1 / (1 + np.exp(-model(tweet, b, new_weights)))
                    for word in tweet:
                        # evaluation of cost function gradient
                        grad_eval = (p - sentiment) + reg * new_weights[word]
                        # take gradient descent step with momenum
                        z = beta * z + grad_eval
                        new_weights[word] = new_weights[word] - gamma * z

                    tweet_counter += 1
            return new_weights

        # gradient descent function
        def gradient_descent_cost(gamma, max_eps, reg, b, w0, beta):
            '''
            performs binary (ridge) logistic regression with gradient descent
            input:
                gamma - float, learning rate
                max_eps - int, maximum number of epochs
                reg - float, ridge penalty value
                b - float, bias
                w0 - dict, dictionary of word, weight pairs for initial weights
            output:
                new_weights - dict, dictionary of word, weight pairs for final weights
                cost_history - list, list of costs at every 10% of dataset gone through
            '''
            # copy initial weights
            new_weights = copy(w0)
            # cost function history container
            cost_history = []

            z = np.zeros((np.shape(w0)))  # momentum term

            for k in range(max_eps):
                # randomly shuffle data at beginning of each epoch
                random.shuffle(training_set)
                tweet_counter = 0
                for instance in training_set:
                    # remove duplicate words in tweet
                    tweet = list(set(instance[0]))
                    sentiment = instance[1]
                    p = 1 / (1 + np.exp(-model(tweet, b, new_weights)))
                    for word in tweet:
                        # evaluation of cost function gradient
                        grad_eval = (p - sentiment) + reg * new_weights[word]
                        # take gradient descent step with momentum
                        z = beta * z + grad_eval
                        new_weights[word] = new_weights[word] - gamma * z

                    tweet_counter += 1
                    if tweet_counter % (len(training_set) / 1) == 0:
                        # record cost
                        if sentiment == 1:
                            cost = pos_cost(tweet, reg, b, new_weights)
                        else:
                            cost = neg_cost(tweet, reg, b, new_weights)
                        cost_history.append(cost)

            return new_weights, cost_history

        def get_accuracy(b, weights):
            '''
            gets accuracy of predictions of weights on the validation set
            input:
                b - float, bias
                weights - dict, dictionary of word, weight pairs for initial weights
            output:
                accuracy - float, validation accuracy
            '''
            misclassifications = 0
            for instance in validation_set:
                tweet = instance[0]
                sentiment = instance[1]
                p = 1 / (1 + np.exp(-model(tweet, b, weights)))
                p = round(p)
                if p != sentiment:
                    misclassifications += 1
            accuracy = 1 - (misclassifications / len(validation_set))
            return accuracy

        best_w, cost_hist = gradient_descent_cost(10 ** -6, 10, 1, -.9, words, 0)
        plot_cost_histories(cost_hist)
        print("final cost:", cost_hist[-1])
        # validation set accuracy
        acc = get_accuracy(-.9, best_w)
        print("accuracy:", acc)

        def test_accuracy(b, weights):
            '''
            gets accuracy of predictions of weights on the test set
            input:
                b - float, bias
                weights - dict, dictionary of word, weight pairs for initial weights
            output:
                test_acc - float, test accuracy
            '''
            misclassifications = 0
            for instance in test_set:
                tweet = instance[0]
                sentiment = instance[1]
                p = 1 / (1 + np.exp(-model(tweet, b, weights)))
                p = round(p)
                if p != sentiment:
                    misclassifications += 1
            test_acc = 1 - (misclassifications / len(test_set))
            return test_acc

        test_accuracy(-.9, best_w)

        print("The value of the bias term b is 0.25.")
        print()
        print("Top 5 words by weight:")
        for word, weight in dict(sorted(best_w.items(), key=operator.itemgetter(1), reverse=True)[:5]).items():
            print(word, ":", weight)
        print()
        print("Bottom 5 words by weight:")
        for word, weight in dict(sorted(best_w.items(), key=operator.itemgetter(1))[:5]).items():
            print(word, ":", weight)

        return (best_w)