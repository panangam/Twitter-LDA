# Twitter and Foursquare data collection and processing modules

This is a collection of python code utilized in a research paper regarding topic modelling of texts ("shouts") from a location-based social network (Foursquare). Data is gathered initially from Twitter tweets gathered from Twitter Streaming API, which are then cross-referenced using Foursquare/Swarm API to retrieve the original shout text. Shouts are then filtered, processed, tokenized, and analyzed using LDA (Latent Dirichlet Allocation) algorithm. The generated LDA model can then be visualized using several techniques. The code assume input data of shouts/check-ins each associated with a user and a "venue." Each venue is a place with name, coordinates, and venue_id. Visualization techniques are primarily used to compare different venues to each other. 

## Requirements

1. Python version 2.7
2. Other dependencies listed in requirements.txt

## Installation

1. Clone repository or download the whole directory and change working directory into the root directory of project
2. Use pip or virtualenv to install dependency listed in requirements.txt

## Hyper parameters

- Tokenization library to use (Twokenize, Gensim, or NLTK Tweet Tokenizer) => (twokenize, gensim, tweet)
- no. of topics 
- no. of passes to run LDA
- Type of alpha (auto, symmetric)

## Visualizations

- Multidimensional scaling (MDS)
- Distance matrix (Hellinger Distance)
    - matplotlib
    - text
- Week-days distribution of Hellinger Distance (?)
- Top terms for each topic

## Modules

Basically a flow of information from top to bottom

___Most files contain hardcoded directory names. Users should make sure that the names are correct before use.___

#### scrape.py

- Collect data from Twitter Streaming API of tweets that 
    - are English
    - contain terms "4sq", "foursquare", or "swarmapp" (hardcoded)
- Usage:
    - edit customer keys, customer secret, token, token secret in the source file
    - can also edit output file name
    - run script as main

#### filter.py

- filter only tweets that 
    - are English
    - have geo data
    - in California
- also split all tweets into files as chunks of 500 tweets each to be used in next step
- Usage:
     - edit file names and directories in file (hardcoded)
     - run script as main

#### twitter2foursquare.py

- read tweets and cross-reference them with Foursquare API shouts data
- 500 requests are made per hour as per Foursquare's API limit
- Usage:
    - edit access token in the file
    - edit file names and directories in file (hardcoded)
    - run script as main

#### transform_shouts.py

- select only important fields from shout data
- Usage:
    - edit file names and run this thing

#### sqlite_models.py

- contain definition for sqlite database model used to store venues information
- also include code to create the database
- Usage:
    - edit file names to read transformed shouts file and run this thing once to insert data into database

#### sqlite_quries.py

- contain scripts to access database and gather information
- also include code to generate an *essential* collection of text files containing data from each venue
- will generate a file for each venue in the /data/ven folder
- Usage:
    - edit file names and run this thing once after a set of data collection to generate files from data base!

#### lda_driver.py

- provide a class "LdaDriver" used to train an LDA model with shouts data collected
- also house the visualization part 
- Usage:
    - create LdaDriver object with desired parameters
        - corpus_type: tokenizer to user (twokenize, gensim, tweet)
        - num_topics: number of topics
        - num_passes: number of passes
        - alpha: type of alpha to use in learning (symmetric, auto)
        - make_corpus: create a corpus for the tokenizer or not (True, False) (use this when using a new tokenizer or new dataset)
        - make_lda: train LDA or not (True, False) (use this when try a new set of parameters; can set to False if just want to visualize)
    - example: 
        ```python
        driver_settings = {'corpus_type':'twokenize',
                           'num_topics':30,
                           'num_passes':20,
                           'alpha':'symmetric',
                           'make_corpus':False,
                           'make_lda':True}
        driver = LdaDriver(**driver_settings)
        ```
    - call methods of LdaDriver for different visualizations
        - .vis_heatmap
        - .vis_MDS
        - .vis_ldavis
        - .print_dist_matrix
    - also functions from the namespace (wow, fancy!)
        - process_temporal_shouts_by_weekday(venue_id)
    - example:
        ```python
        driver.vis_heatmap(driver.dist_matrix, [ven.name for ven in driver.vens])
        driver.vis_MDS(driver.dist_matrix, [ven.name for ven in driver.vens])
        driver.vis_ldavis()
        ```
    - read code comments for more information