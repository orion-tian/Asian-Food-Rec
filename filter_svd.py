from __future__ import print_function
import pandas as pd
import pickle
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize
from scipy.sparse.linalg import svds
import sklearn

import matplotlib
import numpy as np
import matplotlib.pyplot as plt

# read the CSV file
df_recipes = pd.read_csv('recipes_fast_2.csv')
df_user = pd.read_csv('user_data.csv')

documents = []

for index, row in df_recipes.iterrows():
  reviews_ser = df_user[df_user['recipe_id'] == row['id']]['review']
  reviews = ""
  for review in reviews_ser:
     reviews += str(review)
  documents.append((row["name"], row["tags"], 
                    row["steps"], row["description"], reviews))

# np.random.shuffle(documents)

# print("Loaded {} documents".format(len(documents)))
# print("Here is one of them:")
# print(documents[0][0])
# print(documents[0][1])
# print(documents[0][2])
# print(documents[0][3])
# print(documents[0][4])
# print()

# turn documents into term-doc matrix
vectorizer = TfidfVectorizer(stop_words = 'english', max_df = .8, min_df = 1)
td_matrix = vectorizer.fit_transform([x[2] for x in documents])
print("Term-doc matrix shape:")
print(type(td_matrix))
print(td_matrix.shape)
print()

"""# SVD
# u,s,v_trans = svds(td_matrix, k=100)
# print("USV shape:")
# print(u.shape)
# print(s.shape)
# print(v_trans.shape)
# print()
# plt.plot(s[::-1])
# plt.xlabel("Singular value number")
# plt.ylabel("Singular value")
# plt.show()"""

# here's where the magic happens!
# get a k-dimensional representation of documents and words (with k=40)
#      U       sigma       V^T
docs_compressed, s, words_compressed = svds(td_matrix, k=100)
words_compressed = words_compressed.transpose()
"""print("k-dimensional rep of documents and words:")
print(words_compressed.shape)
print(docs_compressed.shape)
print()

word_to_index = vectorizer.vocabulary_
index_to_word = {i:t for t,i in word_to_index.items()}"""

#row normalize
words_compressed_normed = normalize(words_compressed, axis = 1)

"""# cosine similarity
# def closest_words(word_in, words_representation_in, k = 10):
#     if word_in not in word_to_index: return "Not in vocab."
#     sims = words_representation_in.dot(words_representation_in[word_to_index[word_in],:])
#     asort = np.argsort(-sims)[:k+1]
#     return [(index_to_word[i],sims[i]) for i in asort[1:]]

# td_matrix_np = td_matrix.transpose().toarray()
# td_matrix_np = normalize(td_matrix_np)

# word = 'dragon'
# print("Using SVD, closest words to " + word + ":")
# for w, sim in closest_words(word, words_compressed_normed):
#   try:
#     print("{}, {:.3f}".format(w, sim))
#   except:
#     print("word not found")
# print()"""

docs_compressed_normed = normalize(docs_compressed)

"""# this is basically the same cosine similarity code that we used before, just with some changes to
# the returned output format to let us print out the documents in a sensible way
# def closest_projects(project_index_in, project_repr_in, k = 5):
#     sims = project_repr_in.dot(project_repr_in[project_index_in,:])
#     asort = np.argsort(-sims)[:k+1]
#     return [(documents[i][0], documents[i][2], documents[i][3], sims[i]) for i in asort[1:]]

# td_matrix_np = td_matrix.toarray()
# td_matrix_np = normalize(td_matrix_np)

# for i in range(10):
#     print("INPUT PROJECT: "+documents[i][0]+ ": " + documents[i][3])
#     print("CLOSEST PROJECTS:")
#     print("Using SVD:")
#     for title, steps, description, score in closest_projects(i, docs_compressed_normed):
#         print("{}:{}:{:.3f}".format(title, description, score))
#         print()
#     print()
#     print("Using term-document matrix:")
#     for title, steps, description, score in closest_projects(i, td_matrix_np):
#         print("{}:{}:{:.3f}".format(title, description, score))
#         print()
#     print()
#     print("--------------------------------------------------------\n")

# Once again, basically the same cosine similarity code, but mixing two different matrices
# def closest_projects_to_word(word_in, k = 5):
#     if word_in not in word_to_index: return "Not in vocab."
#     sims = docs_compressed_normed.dot(words_compressed_normed[word_to_index[word_in],:])
#     asort = np.argsort(-sims)[:k+1]
#     return [(i, documents[i][0],sims[i]) for i in asort[1:]]

# word = "chicken"
# print("closest projects to word: " + word)
# for i, proj, sim in closest_projects_to_word(word):
#     print("({}, {}, {:.4f}".format(i, proj, sim))
# print()"""

# what if query has multiple words?
query = "frozen dessert"
query_tfidf = vectorizer.transform([query]).toarray()
print("query: " + query)
print("query tf-idf shape:")
print(query_tfidf.shape)
print()
print(np.__version__)
print(sklearn.__version__)
print(pd.__version__)

query_vec = normalize(np.dot(query_tfidf, words_compressed_normed)).squeeze()
print(type(words_compressed_normed))

def closest_projects_to_query(query_vec_in, k = 5):
    sims = docs_compressed_normed.dot(query_vec_in)
    asort = np.argsort(-sims)[:k+1]
    return [(i, documents[i][0],sims[i]) for i in asort[1:]]

print("closest recipes to query: ")
for i, proj, sim in closest_projects_to_query(query_vec):
    print("({}, {}, {:.4f}".format(i, proj, sim))

# so need to store words_compressed_normed and docs_compressed_normed
df_words = pd.DataFrame(words_compressed_normed)
df_docs = pd.DataFrame(docs_compressed_normed)

df_words.to_csv('compressed_words.csv', index=False)
df_docs.to_csv('compressed_docs.csv', index=False)

# with open('compressed_words.pickle', 'wb') as f:
#     pickle.dump(words_compressed_normed, f)
# with open('compressed_docs.pickle', 'wb') as f:
#     pickle.dump(docs_compressed_normed, f)
# with open('documents.pickle', 'wb') as f:
#     pickle.dump(documents, f)


