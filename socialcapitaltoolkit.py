import pandas as pd
import warnings
import nltk
import re

warnings.filterwarnings("ignore")
nltk.download('wordnet')
nltk.download('omw-1.4')
import numpy as np
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import json
import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from utilities.MySQL_Connectivity import connectivity
from utilities.preprocessing import preprocess_text
from nltk.sentiment.vader import SentimentIntensityAnalyzer

db_name = "User_data"
db_host = "localhost"
db_username = "root"
db_password = "Mysql@098"


def socialcapitaltoolkit(pred: str):
    """This function will create clusters:
    - load the training data
    - clean the data
    - catch the user's response
    - create clusters on text
    - perform PCA
    - link api to segregate cluster's topics
    Args:
        pred (str): the input text user has given
    Returns:
        list: response list
        df: having cluster words
        df: having topics based words
    """

    # load the dataset
    # df = pd.read_csv('sub_final.csv', index_col=0)
    df = connectivity(db_name, db_host, db_username, db_password)

    df.dropna(inplace=True)
    # get sentiment of what user has written
    SIA = SentimentIntensityAnalyzer()
    ss = SIA.polarity_scores(pred)
    # load the user's response
    pred = [f'''{pred}''']
    pred_clean = [re.sub("[^A-Za-z]+", " ", ' '.join(pred))]

    pred_data = pd.DataFrame(pred_clean, columns=['Submission_Text'])

    # create df based on submission text
    st = pd.DataFrame(df['Submission_Text'])

    st = st.append(pred_data).reset_index(drop=True)

    # create tf-idf
    answers = st.to_numpy()

    st['cleaned'] = st['Submission_Text'].apply(lambda x: preprocess_text(x, remove_stopwords=True))

    v = TfidfVectorizer(sublinear_tf=True, min_df=0, max_df=0.9)

    x = v.fit_transform(st['cleaned'].values.astype('U'))  ## Even astype(str) would work

    # initialize kmeans with 4 centroids
    kmeans = KMeans(n_clusters=10, random_state=42)

    # fit the model
    fitvar = kmeans.fit(x)

    # store cluster labels in a variable
    clusters = fitvar.labels_

    st['cluster'] = clusters

    # initialize PCA with 2 components
    pca = PCA(n_components=2, random_state=42)

    # pass our X to the pca and store the reduced vectors into pca_vecs
    pca_vecs = pca.fit_transform(x.toarray())

    # save our two dimensions into x0 and x1
    x0 = pca_vecs[:, 0]

    x1 = pca_vecs[:, 1]

    st['x0'] = x0

    st['x1'] = x1

    # store the cluster number
    cluster_number = st['cluster'].iloc[-1]

    def get_top_keywords(n_terms):
        """This function returns the df having keywords for each centroid of the KMeans"""
        df_top = pd.DataFrame(x.todense()).groupby(clusters).mean()  # groups the TF-IDF vector by cluster
        terms = v.get_feature_names_out()  # access tf-idf terms
        clus_dict = {}
        for i, r in df_top.iterrows():
            clus_dict[i] = ','.join([terms[t] for t in np.argsort(r)[-n_terms:]])
        return pd.DataFrame.from_dict(dict(clus_dict), orient='index', columns=['Response']).reset_index().rename(
            columns={"index": "Clusters"})

    # create df based on cluster words
    df_clusters = get_top_keywords(30)
    clusterofresponse = df_clusters[df_clusters['Clusters'] == cluster_number]
    var_list = []
    for i in range(0, len(df_clusters)):
        var_list.append([x.strip() for x in df_clusters['Response'][i].split(',')])

    # convert list into strings
    var = ' '.join(var_list[cluster_number])

    response_list = st['cleaned'].iloc[-1]

    # Call the Rest API and ingest cluster words into it and have the topics based on those words
    #https://www.uclassify.com/browse/uclassify/topics?input=Text
    headers = {
        'Authorization': 'Token 6seBaFNFtzwP',
        'Content-Type': 'application/json',
    }
    json_data = {
        'texts': [
            f'{var}',
        ],
    }

    resp_cluster = requests.post('https://api.uclassify.com/v1/uclassify/topics/classify', headers=headers,
                                 json=json_data)
    dict_output_df = pd.json_normalize(pd.DataFrame(json.loads(resp_cluster.text)[0])['classification'])

    return response_list, dict_output_df, var_list[cluster_number], cluster_number, ss
