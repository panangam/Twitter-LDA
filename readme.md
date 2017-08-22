# Twitter and Foursquare data collection and processing modules

This is a "renovated" collection of python code utilized in a research paper regarding topic modelling of texts ("shouts") from a location-based social network (Foursquare). Data is gathered initially from Twitter tweets gathered from Twitter Streaming API, which are then cross-referenced using Foursquare/Swarm API to retrieve the original shout text. Shouts are then filtered, processed, tokenized, and analyzed using LDA (Latent Dirichlet Allocation) algorithm. The generated LDA model can then be visualized using several techniques. The code assume input data of shouts/check-ins each associated with a user and a "venue." Each venue is a place with name, coordinates, and venue_id. Visualization techniques are primarily used to compare different venues to each other. 

With this restructured code, user can choose to run LDA algorithm on arbitrary collection of texts, or use the original workflow involving Foursquare's venues information with its visualization techniques.

## Requirements

1. Python version 2.7
2. Other dependencies listed in requirements.txt
3. Twitter API access authentications for data scraping (if need to scrape twitter data)
4. Foursquare API access token for checkins referencing (if work with foursquare data)

## Installation

1. Clone repository or download the whole directory and change working directory into the root directory of project.
2. Use pip or virtualenv to install dependency listed in requirements.txt.
3. Create "twitterAuth.json" file containing a json with necessary authentication for Twitter Streaming API. (see format below in Configuration section)

## Typical Usage

Some typical scenarios that this module can be used for are listed here with ther corresponding scripts.

1. Scraping twitter data from Streaming API. (`twitterStreamClient.py`)
2. Filtering twitter data further, in case you are a cute little paranoid. (`filter.py`)
3. Reference appropriate twitter data of shouts from Foursquare with the Foursquare API to get venues information. (`twitter2foursquare.py`)
4. Run LDA algorithm on some collection of texts. (`myDriver.py` or customized driver)
5. Run LDA algorithm on the Foursquare shouts and venues information. (`myDriver.py` or customized driver)
6. Visualize the learnt LDA model with `pyLDAvis` (`myDriver.py` or customized driver)
7. Visualize the Foursquare data with various techniques. (`myDriver.py` or customized driver)

## Configurations

### Database

Change the name of SQLite database file (`.sqlite`) to use in `twitterLda/sqlite_models.py` code directly. Default is `10-27.sqlite`, the original database used in the student's paper.

### Project path

Some paths of the project folder structure are defined in `twitterLda/projectPath.py`. Configure according to your need.

### Twitter Streaming API filter

The `filter` endpoint of the Streaming API is used to scrape data. parameters used to filter the tweets should be configured directly in the file `twitterStreamClient.py`

### twitterAuth.json

Authentication file for accessing Twitter Streaming API. Must contain a JSON with fields `"consumerKey"`, `"consumerSecret"`, `"token"`, and `"tokenSecret"`.

Sample file:

```json
{
  "consumerKey": "ZIJyJlEMxxxxxxxzrPbqLFSnO",
  "consumerSecret": "Xa1Vq8Ze5i7xxxxxxxxxxxxxxxxxmWekiAGPXEoXinhp5opE2",
  "token": "3264530906-hJ0arh1odxxxxxxxxxxxxxxygzA91WNf0",
  "tokenSecret": "VsmPmWdYZ3R2xxxxxxxxxxxxxxxxxxxxxxWpj847y6ms"
}
```

### Foursquare API key

...is specified in the source file `twitter2foursquare.py` directly. Please customize according to your usage. In case you're wondering, no, that's not my own key, and I know making this available to public is stupid. I don't care about the original author who subjected me to endless hours of code refactoring involving a spaghetti ball of convoluted dependencies and overassumptions of usage. Now, I have to wonder whether my effots will simply vanish in vain due to negligence of somebody...

### LDA driver script

The LDA (Laten Dirichlet Allocation) algorithm library is called by a driver script executed from the root directoty. The example code, `myDriver.py` demonstrate basic funcionality of the driver. The driver can be separated into 2 parts: LDA model and visualization.

#### LDA model

LDA model and corpus learning or loading is controlled by several parameters passed to make the driver object: `LdaDriver` from package `twitterLda.lda_driver`. All available parameters are as follow

- project_name: Name of the project. All corpus and model are stored in the directory `data/ldaProjects/{project_name}`
- corpus_type: Type of corpus to used (must be a string one of `twokenize`, `gensim`, or `tweet`).
- num_topics: Number of topics assumed to be present in the corpus.
- num_passes: Number of passes to run the lDA algorithm.
- alpha: Type of alpha to used to learn LDA (must be one of `symetric` or `auto`).
- docIterFunc: Function returning a generator yielding a document from the corpus each time it is iterated. This function will be called multiple times, with each time producing a generator starting at the first document. Several "IterFunc"s are available in package `twitterLda.fileReader`
- make_corpus: (`True, False`) Choose to extract new corpus from the documents or not. If set to `False`, a generated corpus will be used.
- make_lda: (`True, False`) Choose to learn a new LDA model or not. If set to `False`, a learnt model will be loaded.
- make_venues: (`True, False`) ___*Only for shouts information generated by `twitter2foursquare.py` or an output from Foursquare API.___ Choose to generate the database and index of venues present in the dataset. Used for visualizing venues data.

#### Visualization

##### pyLDAvis

A library to visualize any arbitrary model in browser. 

##### Venue visualization

Available visualization techniques:

- Multidimensional scaling (MDS)
- Distance matrix (Hellinger Distance)
    - matplotlib
    - text
- Week-days distribution of Hellinger Distance (?)  
- Top terms for each topic

Look at example driver and `twitterLda/lda_driver.py` for information.