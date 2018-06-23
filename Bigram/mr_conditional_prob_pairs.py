#!/usr/bin/env python

from mrjob.job import MRJob
from mrjob.step import MRStep

class MRConditionalProbability(MRJob):
    def steps(self):
        return [
            MRStep(mapper_init=self.init_get_words,
                    mapper=self.mapper_get_words,
                   combiner=self.combiner_count_words,
                   reducer=self.reducer_count_words),
            MRStep(reducer=self.reducer_find_max_word)
        ]

    def CleanWord(self, aword):
        """
        Function input: A string which is meant to be
           interpreted as a single word.
        Output: a clean, lower-case version of the word
        """
        # Make Lower Case
        aword = aword.lower()
        # Remove special characters from word
        for character in '.,;:\'?':
            aword = aword.replace(character, '')
        # No empty words
        if len(aword) == 0:
            return None
        # Restrict word to the standard english alphabet
        for character in aword:
            if character not in 'abcdefghijklmnopqrstuvwxyz':
                return None
        # return the word
        return aword

    def init_get_words(self):
        self.prevLineLastWord = ''

    def mapper_get_words(self, _, line):
        data_list = line.strip().split()
        if len(data_list) == 0:
            self.prevLineLastWord = ''

        for idx in range(len(data_list)):
            current_word = self.CleanWord(data_list[idx])

            self.wordCounted = False
            if idx == 0 and self.prevLineLastWord != '' and self.prevLineLastWord != None and current_word != None:
                yield (self.prevLineLastWord, current_word), 1
                self.wordCounted = True

            if idx == len(data_list) - 1 and data_list[idx] != None:
                self.prevLineLastWord = data_list[idx]

            if current_word != None:
                yield (current_word,), 1
            # Use CleanWord function to clean up the word
            if idx + 1 < len(data_list):
                next_word = self.CleanWord(data_list[idx + 1])
                if current_word != None and next_word != None:
                    yield (current_word, next_word), 1



    def combiner_count_words(self, word, counts):
        yield word, sum(counts)

    def reducer_count_words(self, word, counts):
        yield  None, (word, sum(counts))

    def reducer_find_max_word(self, _, words):
        #set current word for which you want to calcualte conditional probability
        current_word = 'for'
        c_word_count = 0
        bigrams = {};
        for w in words:
            if w[0][0].lower() == current_word:
                if len(w[0]) == 2:
                    bigrams[','.join(w[0])] = w[1]
                if len(w[0]) == 1:
                    c_word_count += w[1]

        #Sort and get top ten conditionals
        for index, p in enumerate(sorted(bigrams, key=bigrams.get, reverse=True)):
            if index < 10:
                yield p, float(bigrams[p])/float(c_word_count)
            else:
                break


if __name__ == '__main__':

    MRConditionalProbability.run()