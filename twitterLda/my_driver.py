from twitterLda.lda_driver import *
from twitterLda.fileReader import *

if __name__ == '__main__':
    driver_settings = {'corpus_type':'gensim',
                       'num_topics':13,
                       'num_passes':23,
                       'alpha':'symmetric',
                       'docIter':twitterFileReader('data/twitData31.dat'),
                       'make_corpus':True,
                       'make_lda':True}
    driver = LdaDriver(**driver_settings)
    # driver.print_dist_matrix()

    # print process_temporal_shouts_by_weekday('4b8743f6f964a52056b931e3')

    # driver.vis_heatmap(driver.dist_matrix, [ven.name for ven in driver.vens])
    # driver.vis_MDS(driver.dist_matrix, [ven.name for ven in driver.vens])
    driver.vis_ldavis()

