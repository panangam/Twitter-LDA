# -*- coding: utf-8 -*-
from __future__ import absolute_import, division

from twitterLda.my_corpus import MyCorpus
import twitterLda.sqlite_queries as sq
from twitterLda.projectPath import datadir

import codecs
import logging
import matplotlib.pyplot as plt
from gensim import matutils, corpora, models
import numpy as np
import pyLDAvis
from sklearn.manifold import MDS
import pyLDAvis.gensim as pg
import os

logging.basicConfig(format='%(levelname)s : %(message)s', level=logging.DEBUG)

_SQRT2 = np.sqrt(2)  # sqrt(2) with default precision np.float64

class LdaDriver(object):
    """
    Class to create corpora, LDA models, and perform queries on the models.
    """
    def __init__(self, **kwargs):
        """
        Initialize LdaDriver object.

        LdaDriver object has a corpus and lda model either created here or loaded from file.

        :return: self
        :rtype: LdaDriver
        """
        self.project_name = kwargs['project_name']
        self.corpus_type = kwargs['corpus_type']
        self.num_topics = kwargs['num_topics']
        self.num_passes = kwargs['num_passes']
        self.alpha = kwargs['alpha']
        self.docIterFunc = kwargs['docIterFunc']

        # prepare directory for this project
        self.projectdir = os.path.join(datadir, 'ldaProjects', self.project_name)

        if not os.path.exists(self.projectdir):
            os.makedirs(self.projectdir)

        self.corpusdir = os.path.join(self.projectdir, 'corpora')
        self.modeldir = os.path.join(self.projectdir, 'ldaModels')

        if not os.path.exists(self.corpusdir):
            os.makedirs(self.corpusdir)
        if not os.path.exists(self.modeldir):
            os.makedirs(self.modeldir)

        if kwargs['make_corpus']:
            self.cor = MyCorpus(self.docIterFunc, self.corpus_type)
            self.cor.dictionary.save(os.path.join(self.corpusdir, '{}_dictionary.dict'.format(self.corpus_type)))
            corpora.MmCorpus.serialize(os.path.join(self.corpusdir, '{}_corpus.mm'.format(self.corpus_type)),
                                       self.cor,
                                       id2word=self.cor.dictionary,
                                       index_fname=os.path.join(self.corpusdir, '{}_corpus.mm.index'.format(self.corpus_type)),
                                       progress_cnt=1000)
        
        # load corpus from file
        self.cor = corpora.MmCorpus(os.path.join(self.corpusdir, '{}_corpus.mm'.format(self.corpus_type)))
        self.cor.dictionary = corpora.Dictionary.load(os.path.join(self.corpusdir, '{}_dictionary.dict'.format(self.corpus_type)))

        # Train a new LDA
        if kwargs['make_lda']:
            if self.alpha is 'auto':
                self.lda = models.LdaModel(self.cor,
                                           num_topics=self.num_topics,
                                           id2word=self.cor.dictionary,
                                           passes=self.num_passes,
                                           alpha=self.alpha,
                                           eval_every=10,
                                           iterations=50)
            elif self.alpha is 'symmetric':
                self.lda = models.LdaMulticore(self.cor,
                                               num_topics=self.num_topics,
                                               id2word=self.cor.dictionary,
                                               passes=self.num_passes,
                                               alpha=self.alpha,
                                               batch=True,
                                               eval_every=10,
                                               iterations=50)

            # Save LDA model
            self.lda.save(os.path.join(self.modeldir, '{}_lda_{}t_{}p_{}.model'.format(
                self.corpus_type, self.num_topics, self.num_passes, self.alpha)))

        # Load LDA model
        self.lda = models.LdaMulticore.load(os.path.join(self.modeldir, '{}_lda_{}t_{}p_{}.model'.format(
            self.corpus_type, self.num_topics, self.num_passes, self.alpha)))

        # Load venue index
        self.ven_id2i = {}
        with codecs.open(os.path.join(datadir, 'ven_id2i.txt'), 'r', encoding='utf-8') as fin:
            for line in fin:
                line = line.split()
                self.ven_id2i[line[0]] = int(line[1])

        # Load venues for comparison
        if kwargs['make_venues']:
            self.vens = sq.topn_venues()
            self.dist_matrix = self.compare_venues(self.vens)


    def compare_venues(self, venues):
        """
        Compares venues in vens to each other.

        :param venues: venues to compare
        :type vens: [Venue database objects]
        :return: distance matrix
        :rtype: 2d np.ndarray
        """
        ven_offsets = [self.ven_id2i[ven.id] for ven in venues]
        ven_p_dists = [self.lda.get_document_topics(self.cor[i]) for i in ven_offsets]
        ven_p_dists_dense = matutils.corpus2dense(ven_p_dists, self.num_topics, venues.count())
        return self.hellinger_matrix(ven_p_dists_dense)


    def docbows_to_hellinger_matrix(self, bow_corpus):
        """
        Creates distance matrix from docbows in bow_corpus.

        :param bow_corpus: set of documents in BOW representation
        :type bow_corpus: list of BOWs
        :return: matrix of Hellinger distance measures. Mat(i,j) = dist(doc i, doc j)
        :rtype: 2d array of numpy.float64
        """
        size = len(bow_corpus)
        lda_cor = [self.lda.get_document_topics(doc_bow) for doc_bow in bow_corpus]
        lda_cor_matrix = matutils.corpus2dense(lda_cor, self.num_topics, size)
        return self.hellinger_matrix(lda_cor_matrix)


    def hellinger_matrix(self, dense_matrix):
        """
        Calculates pairwise Hellinger distances for columns of dense_matrix

        :param dense_matrix: matrix of probability distributions. Each column is a venue.
        :type dense_matrix: 2d np.ndarray
        :return: distance matrix
        :rtype: 2d np.ndarray
        """
        dense_matrix = dense_matrix.T
        sqrt_dense_matrix = np.sqrt(dense_matrix)
        size = len(dense_matrix)
        dist_matrix = np.ones((size, size))

        for i in range(size):
            sqrt_i = sqrt_dense_matrix[i]
            for j in range(i, size):
                sqrt_j = sqrt_dense_matrix[j]
                dist_matrix[i, j] = np.sqrt(np.sum((sqrt_i - sqrt_j)**2))/_SQRT2
                dist_matrix[j, i] = dist_matrix[i, j]
        return dist_matrix


    def print_dist_matrix(self):
        """
        Prints venue distance matrix.

        :return: None
        :rtype: None
        """
        print("""~-'`'-.,.-'`'.,.-'`'-.,.-'`'-.,.-'`'-.,.-'`'-.,.-'`'-.,.-'`'~""")
        print('                Distance Matrix for Venues')
        print("""~'-.,.-'`'-.,.-'`'-.,.-'`'-.,.-'`'-.,.-'`'-.,.-'`'-.,.-'`'-.~""")
        ven_list = [self.ven_id2i[ven.id] for ven in self.vens]
        print('       | ' + '  '.join('{:<5}'.format(num) for num in ven_list))
        print('-------+' + '----------'*len(ven_list))

        for i, row in enumerate(self.dist_matrix):
            print ('{:>6} | '.format(ven_list[i]) + '  '.join('{:>1.3f}'.format(val) for val in row[:i + 1]))
        print '\n'


    def vis_heatmap(self, dmatrix, ven_names):
        """
        Display heatmap of distance matrix.

        :param dmatrix: distance matrix
        :type dmatrix: 2d np.ndarray
        :param ven_names: names of venues in matrix
        :type ven_names: [str]
        :return: None
        :rtype: None
        """
        data = dmatrix
        labels = ven_names

        # setup plot figure
        plt.style.use('ggplot')
        fig, ax = plt.subplots(subplot_kw=dict(axisbg='#EEEEEE'))
        ax.grid(color='white', linestyle='solid')
        fig = plt.gcf()
        fig.set_size_inches(8, 8, forward=True)
        fig.subplots_adjust(top=0.63, bottom=0.03, left=0.35, right=0.97)

        # plot heatmap
        heatmap = ax.pcolor(data, cmap=plt.get_cmap('bone'), edgecolor='gray')

        # turn off the frame
        ax.set_frame_on(False)

        # set axes ticks/labels
        ax.set_xticks(np.arange(data.shape[0]) + 0.5, minor=False)
        ax.set_yticks(np.arange(data.shape[1]) + 0.5, minor=False)

        ax.invert_yaxis()
        ax.xaxis.tick_top()

        ax.set_xticklabels(labels, minor=False, size='x-small')
        ax.set_yticklabels(labels, minor=False, size='x-small')

        plt.xticks(rotation=90)
        ax.grid(False)

        # turn off ticks
        ax = plt.gca()
        for t in ax.xaxis.get_major_ticks():
            t.tick1On = False
            t.tick2On = False
        for t in ax.yaxis.get_major_ticks():
            t.tick1On = False
            t.tick2On = False
        plt.show()


    def vis_MDS(self, dmatrix, ven_names):
        """
        Displays MDS graph of venues

        :param dmatrix: distance matrix
        :type dmatrix: 2d np.ndarray
        :param ven_names: names of venues in matrix
        :type ven_names: [str]
        :return: None
        :rtype: None
        """
        # setup plot figure
        plt.style.use('ggplot')
        fig, ax = plt.subplots(subplot_kw=dict(axisbg='#EEEEEE'))
        ax.grid(color='white', linestyle='solid')
        fig = plt.gcf()
        fig.set_dpi(100)
        fig.set_size_inches((8.0, 8.0), forward=True)
        plt.subplots_adjust(left=0.10, bottom=0.10, right=0.95, top=0.95)
        plt.gca().grid(True)
        # plt.gca().set_autoscale_on(False)
        plt.axis([-1.0, 1.0, -1.0, 1.0])
        # fig.subplots_adjust(top=0.63, bottom=0.03, left=0.35, right=0.97)

        # get MDS coordinates for venues
        myMDS = MDS(2, verbose=1, n_jobs=-1, dissimilarity='precomputed')
        myMDS.fit(dmatrix)
        points = myMDS.embedding_

        # add column to points for venue categories
        points = np.c_[points, np.zeros(len(points))]
        CONVENTIONS = 1
        THEME_PARKS = 2
        STADIUMS = 3
        AIRPORTS = 4
        airports = [0, 1, 5, 6, 11, 12, 28]
        conventions = [15, 18, 19, 29]
        theme_parks = [2, 8, 17]
        stadiums = [3, 4, 9, 10, 14, 24]
        for ind in airports:
            points[ind, 2] = AIRPORTS
        for ind in conventions:
            points[ind, 2] = CONVENTIONS
        for ind in theme_parks:
            points[ind, 2] = THEME_PARKS
        for ind in stadiums:
            points[ind, 2] = STADIUMS

        # plot the points
        plt.scatter(points[:, 0], points[:, 1], marker='^', c=points[:, 2], s=80, cmap=plt.get_cmap('Paired'))

        # make labels as annotations
        ven_names[0] = 'LAX'
        ven_names[1] = 'SAN'
        ven_names[5] = 'OAK'
        ven_names[6] = 'SNA'
        ven_names[11] = 'BUR'
        ven_names[12] = 'SJC'
        ven_names[28] = 'LGB'
        for label, x, y in zip(ven_names, points[:, 0], points[:, 1]):
            plt.annotate(
                label,
                xy=(x, y), xytext=(0, 5),
                textcoords='offset points', ha='center', va='bottom',
                size='xx-small',
                bbox=dict(boxstyle='round,pad=0.3', fc='cyan', alpha=0.3))
        plt.tick_params(axis='both', which='major', labelsize=6, color='gray')
        plt.tick_params(axis='both', which='minor', labelsize=6, color='gray')

        # turn off ticks
        ax = plt.gca()
        for t in ax.xaxis.get_major_ticks():
            t.tick1On = False
            t.tick2On = False
        for t in ax.yaxis.get_major_ticks():
            t.tick1On = False
            t.tick2On = False

        plt.show()


    def vis_ldavis(self):
        lda_vis_data = pg.prepare(self.lda, self.cor, self.cor.dictionary)
        pyLDAvis.show(lda_vis_data)

# end class LdaDriver


def hellinger_distance(p, q):
    """
    Calculates the Hellinger distance between two probability distributions.

    :param p: 1st probability distribution
    :type p: numpy array
    :param q: 2nd probability distribution
    :type q: numpy array
    :return: number between 0 & 1. Lower numbers indicate higher similarity.
    :rtype: numpy.float64
    """
    return np.sqrt(np.sum((np.sqrt(p) - np.sqrt(q))**2))/_SQRT2

I2DAY = {1:'Mon', 2:'Tue', 3:'Wed', 4:'Thu', 5:'Fri', 6:'Sat', 7:'Sun'}

def process_temporal_shouts_by_weekday(ven_id):
    """
    Splits ven_id up into bins, returns bins in bow format.

    :param ven_id: venue to split
    :type ven_id: str
    :return: dict of BOWs
    :rtype: {ven_id+day: bow}
    """
    # LA_wdays = sq.split_weekdays('4c31476b213c2d7f93cc335d')
    split_bows = {}
    ven_weekdays = sq.split_weekdays(ven_id)
    # for key in sorted(ven_weekdays.keys()):
    #     new_key = '{venID}_{}'.format(ven_id, I2DAY[key])
    #     split_bows[new_key] =


# def print_topics(lda, ntopics, n=10):
#     """
#     Prints the top n words and probabilities from each topic.
#
#     :param lda: LDA model to print topics from
#     :type lda: gensim.models.LDAmodel
#     :param ntopics: number of topics to print
#     :type ntopics: int
#     :param n: number of words to print per topic
#     :type n: int
#     :return: None
#     :rtype: None
#     """
#     for i, topic in enumerate(lda.show_topics(ntopics, n, log=True, formatted=False)):
#         print(u'TOPIC {0}:'.format(i))
#         for (prob, word) in topic:
#             print(u'   {:1.5f}  {}'.format(prob, word))

def tweetIterFunc():
  with open('data/twitDataSmall.dat', 'r') as fin:
    for text in twitterFileReader(fin):
      yield text

if __name__ == '__main__':
    # test code
    driver_settings = {'corpus_type':'twokenize',
                       'num_topics':10,
                       'num_passes':3,
                       'alpha':'symmetric',
                       'docIterFunc':tweetIterFunc, 
                       'make_corpus':True,
                       'make_lda':True}
    driver = LdaDriver(**driver_settings)

    driver.vis_ldavis()