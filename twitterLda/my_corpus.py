# -*- coding: utf-8 -*-
from __future__ import absolute_import, division

from twitterLda.fileReader import unicode_csv_reader
import twitterLda.twokenize as twokenize

import codecs
import os

from gensim import corpora, utils
from nltk.corpus import stopwords
from nltk.tokenize import TweetTokenizer, RegexpTokenizer

import csv

# logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG)
# logging.basicConfig(format='%(levelname)s : %(message)s', level=logging.DEBUG)


class MyCorpus(corpora.MmCorpus):
    """
    Class that creates a gensim-compatible corpus (i.e., an iterable that yields Bag-of-Words versions of documents,
    one at a time). All linguistic pre-processing needs to happen before transforming a document into a BOW.

    :param docIterFunc: generator function yielding a generator of documents
    :param tokenizer:   name of the tokenizer to use (gensim, tweet, twokenize)
    """

    def __init__(self, docIterFunc, tokenizer):
        self.docIterFunc = docIterFunc
        self.tokenizer = tokenizer
        self.dictionary = corpora.Dictionary(self.iter_documents())
        

        # remove tokens that appear in only one document
        self.dictionary.filter_extremes(no_below=2, no_above=1.0, keep_n=None)
        self.dictionary.compactify()


    def __iter__(self):
        for tokens in self.iter_documents():
            yield self.dictionary.doc2bow(tokens)

    
    def iter_documents(self):
        """
        Helper function for MyCorpus.__iter__()
        Iterate over all documents in top_directory, yielding a document (=list of utf8 tokens) at a time.
        """
        for doc in self.docIterFunc():
            tokens = tokenize(doc, self.tokenizer)
            yield tokens
    

# END class MyCorpus

def preprocess(sentence):
    sentence = sentence.lower()
    tokenizer = RegexpTokenizer(r'\w+')
    tokens = tokenizer.tokenize(sentence)
    filtered_words = [w for w in tokens if not w in set(stopwords.words('english'))]
    return " ".join(filtered_words)

def tokenize(s, tokenizer):
    """
    Tokenizes a string. Returns a different list of tokens depending on which tokenizer is used.

    :param s: string to be tokenized
    :type s: str
    :param tokenizer: identifies tokenizer to use
    :type tokenizer: str
    :return: list of tokens
    :rtype: []
    """
    if tokenizer is 'twokenize':
        tokens = twokenize.tokenize(s)
    elif tokenizer is 'gensim':
        tokens = utils.tokenize(s, lower=True)
    elif tokenizer is 'tweet':
        tknzr = TweetTokenizer(preserve_case=False)
        tokens = tknzr.tokenize(s)

    # list of symbols that can end sentences. twokenize has found these to not be attached to another token.
    # (safe to remove)

    # NLTK english stopwords
    stopset = set(stopwords.words('english'))
    custom_stopset = set(['http', 'https', 'co', 't', 'amp'])

    tokens = [tok.lower() for tok in tokens]
    tokenizer = RegexpTokenizer(r'\w+')
    tokens = tokenizer.tokenize(' '.join(tokens))
    tokens = [tok for tok in tokens if tok not in stopset]
    tokens = [tok for tok in tokens if tok not in custom_stopset]
    tokens = [tok for tok in tokens if len(tok) > 1]


    return tokens

from itertools import *

## test code
if __name__ == '__main__':
    with open('../data/disaster.csv', 'r') as fin:
        csvreader = unicode_csv_reader(fin, delimiter='\t')
        docIter = (line[4] for line in csvreader)
        corpus = MyCorpus(docIter, 'twokenize')