from gensim.models import Word2Vec
import nltk
from nltk.stem import WordNetLemmatizer
import gensim.downloader as api
import gensim

import random

W2V_MODEL_PATH = 'data/w2v.model'

def train():
    """
    Train a model on the wordnet corpus and save it into path.
    """
    from gensim.test.utils import common_texts
    from gensim.models import Word2Vec

    model = Word2Vec(sentences=common_texts, vector_size=100, window=5, min_count=1, workers=4)
    model.save(W2V_MODEL_PATH)
    
wv: gensim.models.KeyedVectors = api.load('word2vec-google-news-300')
# model = Word2Vec.load(W2V_MODEL_PATH)
# lemmatizer = WordNetLemmatizer()

sentence = 'My sister just started shouting at me cause i asked her “do you have any dip left” cause I saw Doritos downstairs'
tokens = sentence.split()  # Split the sentence by whitespace

for i in range(len(tokens)):
    if tokens[i] in wv.key_to_index:
        tokens[i] = random.choice(wv.most_similar(tokens[i], topn=10) + [tokens[i]])[0]

# print(tokens)

# Reconstruct the original sentence
word_salad = ' '.join(tokens)
print(word_salad)