import re

def tokenize(text):
  return [x for x in re.findall(r"[a-z]+", text.lower())]
    
def jaccard_similarity(recipes, query):
  """
  input: list of strings, a query string
  returns a list of ranked indices where the indices is the index of highest ranked string
  """
  query_words = set(tokenize(query))
  similarities = []
  for recipe in recipes:
      recipe_words = set(tokenize(recipe))
      intersection = len(query_words.intersection(recipe_words))
      union = len(query_words.union(recipe_words))
      similarity = intersection / union
      similarities.append(similarity)

  ranked_indices = sorted(range(len(similarities)), key=lambda i: similarities[i], reverse=True)

  return ranked_indices
