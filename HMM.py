########################################
# CS/CNS/EE 155 2018
# Problem Set 6
#
# Author:       Andrew Kang
# Description:  Set 6 skeleton code
########################################

# You can use this (optional) skeleton code to complete the HMM
# implementation of set 5. Once each part is implemented, you can simply
# execute the related problem scripts (e.g. run 'python 2G.py') to quickly
# see the results from your code.
#
# Some pointers to get you started:
#
#     - Choose your notation carefully and consistently! Readable
#       notation will make all the difference in the time it takes you
#       to implement this class, as well as how difficult it is to debug.
#
#     - Read the documentation in this file! Make sure you know what
#       is expected from each function and what each variable is.
#
#     - Any reference to "the (i, j)^th" element of a matrix T means that
#       you should use T[i][j].
#
#     - Note that in our solution code, no NumPy was used. That is, there
#       are no fancy tricks here, just basic coding. If you understand HMMs
#       to a thorough extent, the rest of this implementation should come
#       naturally. However, if you'd like to use NumPy, feel free to.
#
#     - Take one step at a time! Move onto the next algorithm to implement
#       only if you're absolutely sure that all previous algorithms are
#       correct. We are providing you waypoints for this reason.
#
# To get started, just fill in code where indicated. Best of luck!

import random
import numpy as np
import string
import pyphen
import re

class HiddenMarkovModel:
    '''
    Class implementation of Hidden Markov Models.
    '''

    def __init__(self, A, O):
        '''
        Initializes an HMM. Assumes the following:
            - States and observations are integers starting from 0. 
            - There is a start state (see notes on A_start below). There
              is no integer associated with the start state, only
              probabilities in the vector A_start.
            - There is no end state.

        Arguments:
            A:          Transition matrix with dimensions L x L.
                        The (i, j)^th element is the probability of
                        transitioning from state i to state j. Note that
                        this does not include the starting probabilities.

            O:          Observation matrix with dimensions L x D.
                        The (i, j)^th element is the probability of
                        emitting observation j given state i.

        Parameters:
            L:          Number of states.
            
            D:          Number of observations.
            
            A:          The transition matrix.
            
            O:          The observation matrix.
            
            A_start:    Starting transition probabilities. The i^th element
                        is the probability of transitioning from the start
                        state to state i. For simplicity, we assume that
                        this distribution is uniform.
        '''

        self.L = len(A)
        self.D = len(O[0])
        self.A = A
        self.O = O
        self.A_start = [1. / self.L for _ in range(self.L)]


    def viterbi(self, x):
        '''
        Uses the Viterbi algorithm to find the max probability state 
        sequence corresponding to a given input sequence.

        Arguments:
            x:          Input sequence in the form of a list of length M,
                        consisting of integers ranging from 0 to D - 1.

        Returns:
            max_seq:    State sequence corresponding to x with the highest
                        probability.
        '''

        M = len(x)      # Length of sequence.

        # The (i, j)^th elements of probs and seqs are the max probability
        # of the prefix of length i ending in state j and the prefix
        # that gives this probability, respectively.
        #
        # For instance, probs[1][0] is the probability of the prefix of
        # length 1 ending in state 0.
        probs = [[0. for _ in range(self.L)] for _ in range(M + 1)]
        seqs = [['' for _ in range(self.L)] for _ in range(M + 1)]

        for i in range(self.L):
            probs[1][i] = self.A_start[i] * self.O[i][x[0]]

        for j in range(2, M+1):
            for i in range(self.L):

                max_value = 0
                max_i = 0

                for k in range(self.L):
                    if probs[j-1][k] * self.A[k][i] * self.O[i][x[j-1]] >= max_value:
                        max_value = probs[j-1][k] * self.A[k][i] * self.O[i][x[j-1]]
                        max_i = k

                probs[j][i] = max_value
                seqs[j][i] = max_i

        max_value = 0
        max_i = 0

        for k in range(self.L):
            if (probs[M][k] > max_value):
                max_value = probs[M][k]
                max_i = k

        s = str(max_i)

        for i in range(M + 1, 1, -1):
            s += str(seqs[i - 1][int(s[len(s) - 1])])

        max_seq = s[::-1]

        return max_seq


    def forward(self, x, normalize=False):
        '''
        Uses the forward algorithm to calculate the alpha probability
        vectors corresponding to a given input sequence.

        Arguments:
            x:          Input sequence in the form of a list of length M,
                        consisting of integers ranging from 0 to D - 1.

            normalize:  Whether to normalize each set of alpha_j(i) vectors
                        at each i. This is useful to avoid underflow in
                        unsupervised learning.

        Returns:
            alphas:     Vector of alphas.

                        The (i, j)^th element of alphas is alpha_j(i),
                        i.e. the probability of observing prefix x^1:i
                        and state y^i = j.

                        e.g. alphas[1][0] corresponds to the probability
                        of observing x^1:1, i.e. the first observation,
                        given that y^1 = 0, i.e. the first state is 0.
        '''

        M = len(x)
        alphas = [[0. for _ in range(self.L)] for _ in range(M + 1)]

        for i in range(self.L):
            alphas[1][i] = self.A_start[i] * self.O[i][x[0]]

        for i in range(1, M):
            for z in range(self.L):
                alphas[i+1][z] = 0

                for j in range(self.L):
                    alphas[i+1][z] += alphas[i][j] * self.A[j][z]

                alphas[i+1][z] *= self.O[z][x[(i+1)-1]]

            if normalize:
                total = sum(alphas[i+1])

                if total != 0:
                    alphas[i+1] = np.divide(alphas[i+1], total)

        return alphas


    def backward(self, x, normalize=False):
        '''
        Uses the backward algorithm to calculate the beta probability
        vectors corresponding to a given input sequence.

        Arguments:
            x:          Input sequence in the form of a list of length M,
                        consisting of integers ranging from 0 to D - 1.

            normalize:  Whether to normalize each set of alpha_j(i) vectors
                        at each i. This is useful to avoid underflow in
                        unsupervised learning.

        Returns:
            betas:      Vector of betas.

                        The (i, j)^th element of betas is beta_j(i), i.e.
                        the probability of observing prefix x^(i+1):M and
                        state y^i = j.

                        e.g. betas[M][0] corresponds to the probability
                        of observing x^M+1:M, i.e. no observations,
                        given that y^M = 0, i.e. the last state is 0.
        '''

        M = len(x)      # Length of sequence.
        betas = [[0. for _ in range(self.L)] for _ in range(M + 1)]

        for i in range(self.L):
            betas[M][i] = 1.0

        for i in range(M - 1, 0, -1):
            for z in range(self.L):
                betas[i][z] = 0

                for j in range(self.L):
                    betas[i][z] += betas[i + 1][j] * self.A[z][j] * self.O[j][x[(i+1)-1]]

            if normalize:
                total = sum(betas[i])

                if total != 0:
                    betas[i] = np.divide(betas[i], total)

        return betas


    def supervised_learning(self, X, Y):
        '''
        Trains the HMM using the Maximum Likelihood closed form solutions
        for the transition and observation matrices on a labeled
        datset (X, Y). Note that this method does not return anything, but
        instead updates the attributes of the HMM object.

        Arguments:
            X:          A dataset consisting of input sequences in the form
                        of lists of variable length, consisting of integers 
                        ranging from 0 to D - 1. In other words, a list of
                        lists.

            Y:          A dataset consisting of state sequences in the form
                        of lists of variable length, consisting of integers 
                        ranging from 0 to L - 1. In other words, a list of
                        lists.

                        Note that the elements in X line up with those in Y.
        '''

        # Calculate each element of A using the M-step formulas.

        for b in range(len(self.A)):
            for a in range(len(self.A[b])):

                numerator = 0
                denominator = 0

                for j in range(len(Y)):
                    for i in range(len(Y[j]) - 1):

                        if Y[j][i + 1] == a and Y[j][i] == b:
                            numerator += 1
                        if Y[j][i] == b:
                            denominator += 1

                if denominator != 0:
                    self.A[b][a] = numerator / denominator
                else:
                    self.A[b][a] = 0

        # Calculate each element of O using the M-step formulas.

        for z in range(len(self.O)):
            for w in range(len(self.O[z])):

                numerator = 0
                denominator = 0

                for j in range(len(Y)):
                    for i in range(len(Y[j])):

                        if X[j][i] == w and Y[j][i] == z:
                            numerator += 1
                        if Y[j][i] == z:
                            denominator += 1

                if denominator != 0:
                    self.O[z][w] = numerator / denominator
                else:
                    self.O[z][w] = 0


    def unsupervised_learning(self, X, N_iters):
        '''
        Trains the HMM using the Baum-Welch algorithm on an unlabeled
        datset X. Note that this method does not return anything, but
        instead updates the attributes of the HMM object.

        Arguments:
            X:          A dataset consisting of input sequences in the form
                        of lists of length M, consisting of integers ranging
                        from 0 to D - 1. In other words, a list of lists.

            N_iters:    The number of iterations to train on.
        '''

        for epoch in range(N_iters):

            A_num = np.zeros((self.L, self.L))
            O_num = np.zeros((self.L, self.D))
            A_denom = np.zeros((self.L, 1))
            O_denom = np.zeros((self.L, 1))

            for p in X:
                M = len(p)

                alphas = self.forward(p, normalize=True)
                betas = self.backward(p, normalize=True)

                for i in range(1, M + 1):

                    total = np.zeros((self.L, 1))

                    for j in range(self.L):
                        total[j] = alphas[i][j] * betas[i][j]

                    total = np.divide(total, sum(total))

                    for k in range(self.L):
                        O_num[k][p[i - 1]] += total[k]
                        O_denom[k] += total[k]

                        if i != M:
                            A_denom[k] += total[k]

                for i in range(1, M):
                    diff = np.zeros((self.L, self.L))

                    for j in range(self.L):
                        for k in range(self.L):
                            diff[j][k] = alphas[i][j] * self.A[j][k] * self.O[k][p[i]] * betas[i + 1][k]

                    diff = np.divide(diff, np.sum(diff))

                    for a in range(self.L):
                        for b in range(self.L):
                            A_num[a][b] += diff[a][b]

            self.A = np.divide(A_num, A_denom)
            self.O = np.divide(O_num, O_denom)


    def generate_emission(self, M):
        '''
        Generates an emission of length M, assuming that the starting state
        is chosen uniformly at random. 

        Arguments:
            M:          Length of the emission to generate.

        Returns:
            emission:   The randomly generated emission as a list.

            states:     The randomly generated states as a list.
        '''

        emission = []
        states = []

        state = np.random.choice(list(range(self.L)))

        for i in range(M):
            state = np.random.choice(list(range(self.L)), p=self.A[state])
            emission.append(np.random.choice(list(range(self.D)), p=self.O[state]))

            states.append(state)

        return emission, states

    ################################################################################
    # CHANGES MADE: ADDED UNIQUE EMISSION FUNCTIONS SPECIFICALLY FOR SONNET GENERATION
    ################################################################################

    def get_syllables(self, word, syl_dict, rem_num_syl):


        word = re.sub('^[^a-zA-Z]*|[^a-zA-Z]*$', '', word)

        if (word.lower() not in syl_dict):
            dic = pyphen.Pyphen(lang='en')
            syl = dic.inserted(word.lower()).split('-')
            return len(syl)

        normal, end = syl_dict[word.lower()]

        for idx in range(len(normal)):
            if normal[idx] <= rem_num_syl:
                return normal[idx]

        if (len(end) != 0):
            for idx in range(len(end)):
                if end[idx] == rem_num_syl:
                    return end[idx]

        return -1
    
    # given a number of syllables, a inverted obs map (obx idx to word), and a syllable dictionary),
    # return indices corresponding to a sonnet
    def generate_sonnet_emission(self, M, inv_obs_map, syl_dict):

        emission = []
        states = []

        syllable_count = 0

        state = np.random.choice(list(range(self.L)))

        while syllable_count < M:
            state = np.random.choice(list(range(self.L)), p=self.A[state])

            choice = -1
            s_count = -1

            while (syllable_count + s_count > M or s_count == -1):
                choice = np.random.choice(list(range(self.D)), p=self.O[state])
                s_count = self.get_syllables(inv_obs_map[choice], syl_dict, M - syllable_count)

            syllable_count += s_count
            emission.append(choice)
            states.append(state)

        return emission, states

    # given a seed word idx (from observation_map), find the state is in
    def find_state(self, seed_word_idx):
        probs = [elem[seed_word_idx] for elem in self.O]

        total = sum(probs)

        probs = [p / total for p in probs]
        rand_uniform = random.uniform(0, 1)

        chosen_state = 0

        while rand_uniform > 0:
            rand_uniform -= probs[chosen_state]
            chosen_state += 1
        return chosen_state - 1

    # given a number of syllables, a inverted obs map (obx idx to word), and a syllable dictionary), and a seed word
    # return indices corresponding to a sonnet in reverse order
    def generate_sonnet_rhyme_emission(self, M, seed_word_idx, inv_obs_map, syl_dict):

        emission = []
        states = []

        syllable_count = 0;

        state = self.find_state(seed_word_idx)

        while syllable_count < M:
            if syllable_count == 0:

                states.append(state)
                emission.append(seed_word_idx)
                syllable_count += self.get_syllables(inv_obs_map[seed_word_idx], syl_dict, M)

                continue

            state = np.random.choice(list(range(self.L)), p=self.A[state])

            choice = -1
            s_count = -1

            while (syllable_count + s_count > M or s_count == -1):
                choice = np.random.choice(list(range(self.D)), p=self.O[state])
                s_count = self.get_syllables(inv_obs_map[choice], syl_dict, M - syllable_count)

            syllable_count += s_count
            emission.append(choice)
            states.append(state)

        return emission, states
    
    ################################################################################
    # END CHANGES
    ################################################################################
    

    def probability_alphas(self, x):
        '''
        Finds the maximum probability of a given input sequence using
        the forward algorithm.

        Arguments:
            x:          Input sequence in the form of a list of length M,
                        consisting of integers ranging from 0 to D - 1.

        Returns:
            prob:       Total probability that x can occur.
        '''

        # Calculate alpha vectors.
        alphas = self.forward(x)

        # alpha_j(M) gives the probability that the state sequence ends
        # in j. Summing this value over all possible states j gives the
        # total probability of x paired with any state sequence, i.e.
        # the probability of x.
        prob = sum(alphas[-1])
        return prob


    def probability_betas(self, x):
        '''
        Finds the maximum probability of a given input sequence using
        the backward algorithm.

        Arguments:
            x:          Input sequence in the form of a list of length M,
                        consisting of integers ranging from 0 to D - 1.

        Returns:
            prob:       Total probability that x can occur.
        '''

        betas = self.backward(x)

        # beta_j(1) gives the probability that the state sequence starts
        # with j. Summing this, multiplied by the starting transition
        # probability and the observation probability, over all states
        # gives the total probability of x paired with any state
        # sequence, i.e. the probability of x.
        prob = sum([betas[1][j] * self.A_start[j] * self.O[j][x[0]] \
                    for j in range(self.L)])

        return prob


def supervised_HMM(X, Y):
    '''
    Helper function to train a supervised HMM. The function determines the
    number of unique states and observations in the given data, initializes
    the transition and observation matrices, creates the HMM, and then runs
    the training function for supervised learning.

    Arguments:
        X:          A dataset consisting of input sequences in the form
                    of lists of variable length, consisting of integers 
                    ranging from 0 to D - 1. In other words, a list of lists.

        Y:          A dataset consisting of state sequences in the form
                    of lists of variable length, consisting of integers 
                    ranging from 0 to L - 1. In other words, a list of lists.
                    Note that the elements in X line up with those in Y.
    '''
    # Make a set of observations.
    observations = set()
    for x in X:
        observations |= set(x)

    # Make a set of states.
    states = set()
    for y in Y:
        states |= set(y)
    
    # Compute L and D.
    L = len(states)
    D = len(observations)


    # Randomly initialize and normalize matrix A.
    A = [[random.random() for i in range(L)] for j in range(L)]

    for i in range(len(A)):
        norm = sum(A[i])
        for j in range(len(A[i])):
            A[i][j] /= norm


    # Randomly initialize and normalize matrix O.
    O = [[random.random() for i in range(D)] for j in range(L)]

    for i in range(len(O)):
        norm = sum(O[i])
        for j in range(len(O[i])):
            O[i][j] /= norm

    # Train an HMM with labeled data.
    HMM = HiddenMarkovModel(A, O)
    HMM.supervised_learning(X, Y)

    return HMM

def unsupervised_HMM(X, n_states, N_iters):
    '''
    Helper function to train an unsupervised HMM. The function determines the
    number of unique observations in the given data, initializes
    the transition and observation matrices, creates the HMM, and then runs
    the training function for unsupervised learing.

    Arguments:
        X:          A dataset consisting of input sequences in the form
                    of lists of variable length, consisting of integers 
                    ranging from 0 to D - 1. In other words, a list of lists.

        n_states:   Number of hidden states to use in training.
        
        N_iters:    The number of iterations to train on.
    '''

    # Make a set of observations.
    observations = set()
    for x in X:
        observations |= set(x)
    
    # Compute L and D.
    L = n_states
    D = len(observations)

    # Randomly initialize and normalize matrix A.
    random.seed(2020)
    A = [[random.random() for i in range(L)] for j in range(L)]

    for i in range(len(A)):
        norm = sum(A[i])
        for j in range(len(A[i])):
            A[i][j] /= norm
    
    # Randomly initialize and normalize matrix O.
    random.seed(155)
    O = [[random.random() for i in range(D)] for j in range(L)]

    for i in range(len(O)):
        norm = sum(O[i])
        for j in range(len(O[i])):
            O[i][j] /= norm

    # Train an HMM with unlabeled data.
    HMM = HiddenMarkovModel(A, O)
    HMM.unsupervised_learning(X, N_iters)

    return HMM
