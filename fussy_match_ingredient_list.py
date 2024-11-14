import requests
import json
import os
from rapidfuzz import process, fuzz

#Use Fuzzy search to get the matched food code for CNF API
#https://pypi.org/project/fuzzywuzzy/

#From CNF API
FOOD_CODE_URL = "https://food-nutrition.canada.ca/api/canadian-nutrient-file/food/?lang=en&type=json"
DATASET_PATH = 'datasets'
os.makedirs(DATASET_PATH, exist_ok=True)

#Load Ingredient food_code dataset
def get_food_code_dataset():
    res = requests.get(FOOD_CODE_URL)
    food_code_data = res.json()
    food_code_filename = 'CNF_API_food_code.json'
    file_name_food_code = f"{DATASET_PATH}/{food_code_filename}"
    with open(file_name_food_code, "w") as f:
        json.dump(food_code_data, f, indent=4)
    
    return food_code_data

def get_fuzzy_match_list(ingre_name,food_descriptions_list,min_score_threshold):
    
    #all matches for the input ingredient
    ingredient_matches = {}
    
    matches = process.extract(
        ingre_name.lower().replace("-"," "),
        [desc for desc, code in food_descriptions_list],
        scorer=fuzz.token_set_ratio,
        limit=10  # Limit the number of matches to top 10
    )
    
    # include those above the threshold
    filtered_matches = [
        (eachMatch[0], eachMatch[1], next(code for desc, code in food_descriptions_list if desc == eachMatch[0]))
        for eachMatch in matches if eachMatch[1] >= min_score_threshold
    ]
    
    # Store the matches for the current ingredient
    ingredient_matches[ingre_name] = filtered_matches
    
    return ingredient_matches
    
def get_fuzzy_match_exactOne(ingre_name,food_descriptions_list,min_score_threshold):    
  
    best_match = process.extractOne(
        ingre_name.lower().replace("-"," "),
        [desc for desc, code in food_descriptions_list],
        scorer=fuzz.token_set_ratio
    )
    
    return_match={}
    # Check if the best match meets the threshold
    if best_match and best_match[1] >= min_score_threshold:
        # Retrieve the food code
        matching_food_code = next(code for desc, code in food_descriptions_list if desc == best_match[0])
        return_match[ingre_name] = {
            "description": best_match[0],
            "score": best_match[1],
            "food_code": matching_food_code
        }
    else:
        # No match above the threshold
        return_match[ingre_name] = None
    
    return return_match
    

def get_match_food_codes(ingre_name, food_code_dataset,min_score_threshold,matchMode):
  
    food_descriptions = [(eachCode['food_description'].lower(), eachCode['food_code']) for eachCode in food_code_dataset]
    
    match matchMode:
        case "Best_Match":
            matched_result=get_fuzzy_match_exactOne(ingre_name,food_descriptions,min_score_threshold) 
        case "List_Match":
            matched_result = get_fuzzy_match_list(ingre_name,food_descriptions,min_score_threshold)
        case _:
            return None


    return matched_result


def test_food_code_fuzzy():     
        
    food_code_dataset = get_food_code_dataset()
    test_ingre_name = 'Boneless rib-eye'
    min_score_threshold=50

    test_matchMode= "Best_Match"
    #test_matchMode= "List_Match"

    ingredient_match = get_match_food_codes(test_ingre_name, 
                                                    food_code_dataset,
                                                    min_score_threshold,
                                                    test_matchMode)

    print("Best Match for Each Ingredient:")
    for ingredient, match in ingredient_match.items():
        if match:
            print(f"Ingredient: {ingredient}")
            print(f"  Description: {match['description']}, Score: {round(match['score'],4)}, Food Code: {match['food_code']}")
        else:
            print(f"Ingredient: {ingredient} - No match found above threshold.")
            
    # # For testing only : best best match by list
    # print("Ingredient to Food Code Matches:")
    # for ingredient, matches in ingredient_match_list.items():
    #     print(f"\nIngredient: {ingredient}")
    #     for description, score, food_code in matches:
    #         print(f"  Description: {description}, Score: {round(score,4)}, Food Code: {food_code}")

#test_food_code_fuzzy()