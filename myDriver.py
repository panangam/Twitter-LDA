from twitterLda.lda_driver import *
from twitterLda.fileReader import tweetIterFuncGen, unicode_csv_reader, venIterFunc
from codecs import open

if __name__ == '__main__':
  with open('data/shouts/test_shouts.txt', 'r', encoding='utf8') as fin:
    driver_settings = {'project_name':'test_venue',
                       'corpus_type':'twokenize',
                       'num_topics':10,
                       'num_passes':3,
                       'alpha':'symmetric',
                       'docIterFunc': venIterFunc,
                       'make_corpus':True,
                       'make_lda':True,
                       'make_venues': True}

    driver = LdaDriver(**driver_settings)
    driver.print_dist_matrix()

    print process_temporal_shouts_by_weekday('4b8743f6f964a52056b931e3')

    driver.vis_heatmap(driver.dist_matrix, [ven.name for ven in driver.vens])
    driver.vis_MDS(driver.dist_matrix, [ven.name for ven in driver.vens])
    driver.vis_ldavis()