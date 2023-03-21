import pandas as pd
from collections import Counter
import matplotlib.pyplot as plt
import ast

df = pd.read_csv('filtered_dataset.csv')

#create plot for most common tags
tags_list = []
for tag in df['tags']:
    for tag in tag.split(','):
        tags_list.append(tag.strip())

# count the frequency of each ingredient
tag_counts = Counter(tags_list)
top_10_tags = tag_counts.most_common(10)
labels, values = zip(*top_10_tags)
plt.bar(labels, values)
plt.title('Top 10 Most Common Tags')
plt.xlabel('Tags')
plt.ylabel('Counts')
plt.xticks(rotation=45, ha='right')
plt.show()


# create plot for most common ingredients
ingredients_list = []
for ingredients in df['ingredients']:
    for ingredient in ingredients.split(','):
        ingredients_list.append(ingredient.strip())

ingredient_counts = Counter(ingredients_list)
top_10_ingredients = ingredient_counts.most_common(10)
labels, values = zip(*top_10_ingredients)
plt.bar(labels, values)
plt.title('Top 10 Most Common Ingredients')
plt.xlabel('Ingredients')
plt.ylabel('Counts')
plt.xticks(rotation=45, ha='right')
plt.show()


#plot for time
plt.hist(df['minutes'], bins=20, range=(0, 180))
plt.title('Distribution of Cooking Times')
plt.xlabel('Time (minutes)')
plt.ylabel('Frequency')
plt.show()

avg_time = df['minutes'].describe()
print("Distribution of time needed: ")
print(avg_time)


#average caloric intake
parse_nutrition = lambda nutrition_str: ast.literal_eval(nutrition_str)
parsed_nutrition = df['nutrition'].apply(parse_nutrition)
nutrition_stats = parsed_nutrition.apply(lambda x: x[0]).describe()

print("Distribution of the nutrition values:")
print(nutrition_stats)