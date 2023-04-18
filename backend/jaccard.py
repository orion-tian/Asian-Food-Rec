import re

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
