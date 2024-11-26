import json
import random
from collections import Counter


MIN_LONG_RECIPE_LEN = 900 #call the get_average_instruction_length() to get a sense

#Get recipe dataset
#long_percnt !=0: Return a long reicpe dataset with samp_size*long_percnt number of recipes, and a short recipe dataset with {1-long_percnt}*samp_size of recipes
#long_percnt ==0: Return a testing dataset with recipes randomly selected between long and short recipes 

def get_testing_dataset(in_filename,samp_size,long_percnt=0):

    with open(in_filename, "r") as f:
        recipe_data = json.load(f)
    
    #Basic filter: instruction!=None
    recipe_data = {recipe_ID: recipe_value for recipe_ID, recipe_value in recipe_data.items() 
                    if recipe_value.get("instructions") and isinstance(recipe_value["instructions"], str) and recipe_value["instructions"].strip()}
 
    if long_percnt!=0:   
        long_recipes={}
        short_recipes={}
        for recipe_ID, recipe_value in recipe_data.items():
            if  len(recipe_value["instructions"]) >= MIN_LONG_RECIPE_LEN:
                long_recipes[recipe_ID] = recipe_value
            else:
                short_recipes[recipe_ID] = recipe_value
        
        num_sample_long = int(samp_size * long_percnt)
        num_sample_short = samp_size - num_sample_long
        
        #corner case check
        if num_sample_long==0:
            raise ValueError("Error: The dataset don't have enough long recipes or the sample size is too small.")
        else:
            print(f"The dataset will contains {num_sample_long} long recipes and {num_sample_short} short recipes.")
              
        sampled_long_items = random.sample(list(long_recipes.items()), min(num_sample_long, len(long_recipes)))
        sampled_short_items = random.sample(list(short_recipes.items()), min(num_sample_short, len(short_recipes)))

        return sampled_short_items,sampled_long_items
    else:
        sampled_items = random.sample(list(recipe_data.items()), samp_size)
        return sampled_items,None

def filter_recipe_ingre_frequency(recipes_list, min_freq=3):
 
    # Get frequency for each ingredient
    ingredient_counts = Counter()
    for eachRecipe in recipes_list:
        ingredients = eachRecipe.get("processed_output", {}).get("pure_ingredients", [])
        ingredient_counts.update(ingredients)
    
    # filter out low frequency recipes
    valid_ingredients = set()
    for eachIngre,count in ingredient_counts.items():
        if count >= min_freq:
            valid_ingredients.add(eachIngre)
        else:
            print(f"[{eachIngre}] Filtered out")
    
    #Filter recipes
    filtered_recipes = []
    for recipe in recipes_list:
        ingredients = recipe.get("processed_output", {}).get("pure_ingredients", [])
        if all(ingredient in valid_ingredients for ingredient in ingredients):
            filtered_recipes.append(recipe)
    
    return filtered_recipes

    
    
'''
Small Helpers
'''  
#Get the average recipe length (the instruction field) in a dataset
def get_average_instruction_length(recipe_filename):
    with open(recipe_filename, "r") as f:
        recipe_data = json.load(f)
    
    instruction_lengths = [len(eachRecipe["instructions"]) for eachRecipe in recipe_data.values()]
    average_length = sum(instruction_lengths) / len(instruction_lengths) if instruction_lengths else 0

    return average_length

def save_json_file(in_data,output_file_name):
    with open(output_file_name, "w") as f:
        json.dump(in_data, f, indent=4)

def get_long_short_recipe_dataset(recipe_filename,sample_size,output_file_name,long_recipe_percnt=0.2):
        #output recipes contains a special percentage of long recipes
        short_recipes,long_recipes = get_testing_dataset(recipe_filename,sample_size,long_percnt=long_recipe_percnt)
        sampled_data = dict(short_recipes + long_recipes)
        save_json_file(sampled_data,output_file_name)
        print(f"{sample_size} records have been saved to {output_file_name}.")

def get_rand_recipe_dataset(recipe_filename,sample_size,output_file_name,long_recipe_percnt=0):
        #output recipes are randomly selected between long and short 
        all_recipes,_ = get_testing_dataset(recipe_filename,sample_size,long_percnt=long_recipe_percnt)
        sampled_data = dict(all_recipes)
        save_json_file(sampled_data,output_file_name)
        print(f"{sample_size} records have been saved to {output_file_name}.")

def get_ingre_list_from_dataset(file_path):
    with open(file_path, 'r') as f:
        processed_recipe_list = json.load(f)
    
    all_ingredients = set() #unique set

    for eachRecipe in processed_recipe_list:
        pure_ingredients = eachRecipe["processed_output"].get("pure_ingredients", [])
        # less_important_ingredients = eachRecipe["processed_output"].get("less_important_ingredients", [])

        all_ingredients.update(pure_ingredients)
        # all_ingredients.update(less_important_ingredients)


    all_ingredients_list = sorted(all_ingredients)
    
    return all_ingredients_list

'''
Testing helpers 
'''
def test_get_average_instruction_length():
    recipe_filename = f'./datasets/sample_data_1000.json'
    avg_len = get_average_instruction_length(recipe_filename)
    print(f"The average instruction length in the {recipe_filename} dataset is: {avg_len:.4f} characters.")

def test_get_testing_dataset(long_recipe_percnt):
    sample_size = 300
    recipe_filename = './recipes_raw/recipes_raw_nosource_fn.json'
    output_file_name = f'./datasets/recipe_dataset_init_{sample_size}.json'
    
    if long_recipe_percnt>0:
        get_long_short_recipe_dataset(recipe_filename,sample_size,output_file_name,long_recipe_percnt=long_recipe_percnt)
        
    else:
        #output recipes are randomly selected between long and short 
        get_rand_recipe_dataset(recipe_filename,sample_size,output_file_name,long_recipe_percnt=0)

def test_filter_recipe_ingre_frequency():
    recipe_filename = f'./datasets/processed_recipes_init_300.json'
  
    with open(recipe_filename, "r") as f:
        recipe_data = json.load(f)
    
    min_freq=2
    filtered_recipes = filter_recipe_ingre_frequency(recipe_data, min_freq=2)
    filtered_filename = f'./datasets/processed_freq{min_freq}_recipes_init_{len(filtered_recipes)}.json'
    save_json_file(filtered_recipes,filtered_filename)
    
        
   
#test_filter_recipe_ingre_frequency()
