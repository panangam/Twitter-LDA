import twitterLda.sqlite_queries as sq

# connect to database defined in twitterLda.sqlite_models
sq.connect() 

# insert shouts from a text file containing json form API into database
with open('data/shouts/test_shouts.txt') as fin:
  sq.insertShoutsFromJson(fin)

# generate helper venues documents
sq.venues_to_docs()

# print top 50 venues with most shouts for verification
topn = sq.topn_venues(50)
topnIDs = ['{}'.format(n.id) for n in topn]
print topnIDs

# generate index of venues (don't ask me why)
sq.make_ven_index()

# disconnect from database
sq.close()