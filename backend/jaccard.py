import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize
import numpy as np
import pickle

with open('compressed_words.pickle', 'rb') as f:
    words_compressed_normed = pickle.load(f) 
with open('compressed_docs.pickle', 'rb') as d:
  docs_compressed_normed = pickle.load(d) 
with open('documents.pickle', 'rb') as d:
  documents = pickle.load(d) 

vectorizer = TfidfVectorizer(stop_words = 'english', max_df = .8, min_df = 1)
vectorizer.fit_transform([x[2] for x in documents])

def tokenize(text):
  return [x for x in re.findall(r"[a-z]+", text.lower())]
    
def jaccard_similarity(descriptions, ratings, query):
  """
  input: list of strings, a query string
  returns a list of ranked indices where the indices is the index of highest ranked string
  """

  # rating ranges from 0-5 while jaccard range much smaller 
  # so make ratings_weight quite smaller to make around same range
  ratings_weight = 0.01
  jaccard_weight = 1.5

  query_words = set(tokenize(query))
  similarities = []
  for description in descriptions:
      recipe_words = set(tokenize(description))
      intersection = len(query_words.intersection(recipe_words))
      union = len(query_words.union(recipe_words))
      similarity = intersection / union
      similarities.append(similarity)
  
  scores = [ratings_weight*ratings[i] + jaccard_weight*similarities[i] for i in range(len(similarities))]

  ranked_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)

  return ranked_indices

def svd_similarity(recipe_rows, ratings, query, k=15):
  """ demo svd code based on index of recipe, so use recipe's rows, 
    k = how many results to return """

  ratings_weight = 0.05
  svd_weight = 1.0

  if query == "":
    return [i for i in range(k+1)]

  query_tfidf = vectorizer.transform([query]).toarray()
  
  query_vec = normalize(np.dot(query_tfidf, words_compressed_normed)).squeeze()

  sims = docs_compressed_normed.dot(query_vec)
  
  svd_scores = np.array([svd_weight*sims[r] for r in recipe_rows])
  rating_scores = np.array([ratings_weight*ratings[i] for i in range(len(recipe_rows))])
  scores = np.add(svd_scores, rating_scores)
  
  asort = np.argsort(-scores)[:k+1]

  return asort

