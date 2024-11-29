"""
Provide functions to evaluate the healthiness of recipes using RAG
"""
"""
need to install the following packages:
pip install -qU langchain-openai
pip install jq
pip install langchain-community
pip install langchain-chroma
"""
import json
from langchain_community.document_loaders import JSONLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from openai import OpenAI
from pathlib import Path
from pprint import pprint

"""
load data from the file "ingredient_nutrient_map.json"
"""


def metadata_fuc(record: dict, metadata: dict) -> dict:
    metadata["ingredient_name"] = record.get("ingredient_name")
    # change the attribute "nutrients" from list to string for the following embedding and vector storage
    metadata["nutrients"] = ''.join(map(str, record.get("nutrients")))
    return metadata


def map_loader(file_path):
    loader = JSONLoader(
        file_path=file_path,
        jq_schema=".[]",
        content_key="ingredient_name",
        metadata_func=metadata_fuc
    )
    data = loader.load()
    return data


"""
split the document into chunks for embedding and vector storage,
then turn the VectorStore into a Retriever
"""


def get_retriever(data, search_k):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=200, add_start_index=True
    )
    all_splits = text_splitter.split_documents(data)
    vectorstore = Chroma.from_documents(documents=all_splits, embedding=OpenAIEmbeddings())
    retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": search_k})
    return retriever


"""
Retrieve the most similar ingredient and its nutrients
"""


def retrieve_ingredient_nutrients(retriever, query):
    results = retriever.get_relevant_documents(query)
    if not results:
        return None, None
    best_match = results[0]
    ingredient_name = best_match.metadata.get("ingredient_name")
    nutrients = best_match.metadata.get("nutrients")

    return ingredient_name, nutrients


"""
Generate
"""


def get_API_response(client, sys_prompt, user_prompt, temp, topp):
    completion = client.chat.completions.create(
        model="gpt-4o",
        temperature=temp,
        top_p=topp,
        messages=[
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": user_prompt}
        ],
    )
    response = completion.choices[0].message.content
    return response


def get_health_score_with_rag(client, retriever, temp, topp, recipe_name, recipe_ingredients,
                              recipe_pure_ingredients):
    ingredients = json.loads(recipe_pure_ingredients)
    nutrient_map = []
    # According to the ingredients in the recipe, retrieve the corresponding nutrients
    for ingredient in ingredients:
        matched_food, nutrients = retrieve_ingredient_nutrients(retriever, ingredient)
        nutrient_map.append(nutrients)

    if not nutrient_map:
        return {
            "error": "No relevant nutrient map found for the given ingredient name."
        }
    sys_prompt = ""
    user_prompt = f"""
    You are a helpful assistant that can evaluate the recipes' healthiness.
    You only need to consider 7 key macronutrients and their ranges to assess a recipe’s healthiness:
    Proteins: 10%-15% of total energy
    Carbohydrates: 55%-75% of total energy
    Sugars: less than 10% of total energy
    Sodium: less than 5 grams
    Fats: 15%-30% of total energy
    Saturated Fats: less than 10% of total energy
    Fibers: more than 25 grams

    Here's the recipe:
    Recipe Title: {recipe_name}
    Ingredients and Measurements: {recipe_ingredients}
    Nutrient Map: {nutrient_map}

    Follow the instructions of the evaluation metric to calculate the health score:
    1. Find the 7 key macronutrients of each ingredient in the nutrient map. Add up nutrients of the same type to get the total content of each nutrient
    2. For each nutrient, evaluate whether its amount in the recipe falls within the given range.
    3. Assign 1 point for each nutrient that falls within the range, and 0 points for each nutrient that falls out of the range.
    4. Add all the points to get the health score. The range of the health score is from 0 to 7.
    Calculate the health score. The output should only contain the following attributes:
    - recipe_title: the recipe name.
    - summary_of_points: name of the key macronutrients and their corresponding points.
    - total_health_score: the number of the total health score.
    The output must be a string in JSON format that contains the above attributes. Do not specify the format type(i.e. json) at the beginning of the output.
    """
    response = get_API_response(client, user_prompt, user_prompt, temp, topp)
    return response

"""
Process every recipe to evaluate healthiness
Add the evaluation into recipe JSON file as attributes
"""
def proceee_recipe_with_rag(client,retriever,input_file_path,output_file_path,temp,topp):
    with open(input_file_path, "r") as file:
        recipes = json.load(file)
    # extract recipe title and ingredient list
    for i, recipe in enumerate(recipes):
        recipe_name = recipe["recipe_title"]
        recipe_ingredients = json.dumps(recipe["ingredients"], indent=4)
        recipe_pure_ingredients = json.dumps(recipe["processed_output"]["pure_ingredients"], indent=4)
        # print(recipe_ingredients)
        # print(recipe_pure_ingredients)

        response = get_health_score_with_rag(client, retriever, temp, topp, recipe_name,
                                             recipe_ingredients, recipe_pure_ingredients)
        try:
            response_data = json.loads(response)
            recipe["summary_of_points"] = response_data.get("summary_of_points")
            recipe["total_health_score"] = response_data.get("total_health_score")
        except json.JSONDecodeError:
            recipe["summary_of_points"] = "Error in processing"
            recipe["total_health_score"] = "Error in processing"
    with open(output_file_path, "w") as file:
        json.dump(recipes, file, indent=4)

    print("health score has been saved")

"""
An example to use the functions
"""

if __name__ == "__main__":
    api_key = "MY_API_KEY"
    temp = 1.0
    topp = 1.0
    health_score_client = OpenAI(api_key=api_key)

    file_path = 'ingredient_nutrient_map.json'
    data = map_loader(file_path)
    search_k = 1  # only want to find the most similar ingredient in the ingredient-nutrient map
    retriever = get_retriever(data, search_k)

    recipe_name = "Double Baked Horseradish Potatoes"
    recipe_ingredients = """[
                "4 large Russet potatoes, scrubbed",
                "2 tablespoons olive oil",
                "1 stick unsalted butter",
                "1/2 cup milk",
                "1/2 cup cream",
                "1/4 cup grated fresh horseradish",
                "Salt and pepper",
                "Sour cream",
                "Chives",
                "4 tablespoons osetra caviar"
            ]"""
    recipe_pure_ingredients = """[
      "potatoes",
      "olive oil",
      "milk",
      "cream",
      "grated fresh horseradish",
      "salt",
      "pepper",
      "chives",
      "osetra caviar"
    ]"""
    response = get_health_score_with_rag(health_score_client, retriever,temp, topp, recipe_name, recipe_ingredients,
                                         recipe_pure_ingredients)
    print(response)


"""
An example to change the recipe JSON file
"""
if __name__ == "__main__":
    api_key = "MY_API_KEY"
    temp = 1.0
    topp = 1.0
    health_score_client = OpenAI(api_key=api_key)

    input_file_path="test_processed_recipes.json"
    output_file_path="test_processed_recipes_with_WHOscore.json"
    nutrient_map_path = 'ingredient_nutrient_map.json'
    data = map_loader(nutrient_map_path)
    search_k = 1  # only want to find the most similar ingredient in the ingredient-nutrient map
    retriever = get_retriever(data, search_k)

    proceee_recipe_with_rag(health_score_client,retriever, input_file_path, output_file_path, temp, topp)