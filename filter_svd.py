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
  documents.append((row["name"], str(row["tags"]), str(row["tags"])+row['name']+str(row["steps"])+str(row["description"]), reviews))

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

with open('compressed_words.pickle', 'wb') as f:
    pickle.dump(words_compressed_normed, f)
with open('compressed_docs.pickle', 'wb') as f:
    pickle.dump(docs_compressed_normed, f)
with open('documents.pickle', 'wb') as f:
    pickle.dump(documents, f)

"""CREATE TABLE `compr_words` (
  `0` float(18,17) NOT NULL,
  `1` float(18,17) NOT NULL,
  `2` float(18,17) NOT NULL,
  `3` float(18,17) NOT NULL,
  `4` float(18,17) NOT NULL,
  `5` float(18,17) NOT NULL,
  `6` float(18,17) NOT NULL,
  `7` float(18,17) NOT NULL,
  `8` float(18,17) NOT NULL,
  `9` float(18,17) NOT NULL,
  `10` float(18,17) NOT NULL,
  `11` float(18,17) NOT NULL,
  `12` float(18,17) NOT NULL,
  `13` float(18,17) NOT NULL,
  `14` float(18,17) NOT NULL,
  `15` float(18,17) NOT NULL,
  `16` float(18,17) NOT NULL,
  `17` float(18,17) NOT NULL,
  `18` float(18,17) NOT NULL,
  `19` float(18,17) NOT NULL,
  `20` float(18,17) NOT NULL,
  `21` float(18,17) NOT NULL,
  `22` float(18,17) NOT NULL,
  `23` float(18,17) NOT NULL,
  `24` float(18,17) NOT NULL,
  `25` float(18,17) NOT NULL,
  `26` float(18,17) NOT NULL,
  `27` float(18,17) NOT NULL,
  `28` float(18,17) NOT NULL,
  `29` float(18,17) NOT NULL,
  `30` float(18,17) NOT NULL,
  `31` float(18,17) NOT NULL,
  `32` float(18,17) NOT NULL,
  `33` float(18,17) NOT NULL,
  `34` float(18,17) NOT NULL,
  `35` float(18,17) NOT NULL,
  `36` float(18,17) NOT NULL,
  `37` float(18,17) NOT NULL,
  `38` float(18,17) NOT NULL,
  `39` float(18,17) NOT NULL,
  `40` float(18,17) NOT NULL,
  `41` float(18,17) NOT NULL,
  `42` float(18,17) NOT NULL,
  `43` float(18,17) NOT NULL,
  `44` float(18,17) NOT NULL,
  `45` float(18,17) NOT NULL,
  `46` float(18,17) NOT NULL,
  `47` float(18,17) NOT NULL,
  `48` float(18,17) NOT NULL,
  `49` float(18,17) NOT NULL,
  `50` float(18,17) NOT NULL,
  `51` float(18,17) NOT NULL,
  `52` float(18,17) NOT NULL,
  `53` float(18,17) NOT NULL,
  `54` float(18,17) NOT NULL,
  `55` float(18,17) NOT NULL,
  `56` float(18,17) NOT NULL,
  `57` float(18,17) NOT NULL,
  `58` float(18,17) NOT NULL,
  `59` float(18,17) NOT NULL,
  `60` float(18,17) NOT NULL,
  `61` float(18,17) NOT NULL,
  `62` float(18,17) NOT NULL,
  `63` float(18,17) NOT NULL,
  `64` float(18,17) NOT NULL,
  `65` float(18,17) NOT NULL,
  `66` float(18,17) NOT NULL,
  `67` float(18,17) NOT NULL,
  `68` float(18,17) NOT NULL,
  `69` float(18,17) NOT NULL,
  `70` float(18,17) NOT NULL,
  `71` float(18,17) NOT NULL,
  `72` float(18,17) NOT NULL,
  `73` float(18,17) NOT NULL,
  `74` float(18,17) NOT NULL,
  `75` float(18,17) NOT NULL,
  `76` float(18,17) NOT NULL,
  `77` float(18,17) NOT NULL,
  `78` float(18,17) NOT NULL,
  `79` float(18,17) NOT NULL,
  `80` float(18,17) NOT NULL,
  `81` float(18,17) NOT NULL,
  `82` float(18,17) NOT NULL,
  `83` float(18,17) NOT NULL,
  `84` float(18,17) NOT NULL,
  `85` float(18,17) NOT NULL,
  `86` float(18,17) NOT NULL,
  `87` float(18,17) NOT NULL,
  `88` float(18,17) NOT NULL,
  `89` float(18,17) NOT NULL,
  `90` float(18,17) NOT NULL,
  `91` float(18,17) NOT NULL,
  `92` float(18,17) NOT NULL,
  `93` float(18,17) NOT NULL,
  `94` float(18,17) NOT NULL,
  `95` float(18,17) NOT NULL,
  `96` float(18,17) NOT NULL,
  `97` float(18,17) NOT NULL,
  `98` float(18,17) NOT NULL,
  `99` float(18,17) NOT NULL
)"""