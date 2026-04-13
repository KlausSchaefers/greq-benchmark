import pandas
import json
df = pandas.read_csv("data/food.csv")
print(df.columns)

for row in df.itertuples():
    name = row[2]
    file_name= row[5].lower().replace(" ", "_")
    ingredients = "\n".join(row[3].replace("[", "").replace("]", "").replace("'", "").split(","))
    steps = row[4]

    content = f"""# {name}
## Ingredients: 
{ingredients}
## Steps: 
{steps}
"""
    try:
        with open(f"data/food/{file_name}.md", "w") as f:
             f.write(content)
        #print(ingredients)
    except Exception as e:
        print(f"Error writing file for {name}: {e}")