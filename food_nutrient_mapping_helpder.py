import requests
import json
import os

# Canadian Nutrient (CNF) API endpoints
#https://produits-sante.canada.ca/api/documentation/cnf-documentation-en.html#a6
NUTRITION_BASE_URL = 'https://food-nutrition.canada.ca'
REQ_LANG='en'
REQ_NUT_AMOUNT = '/api/canadian-nutrient-file/nutrientamount'
#For output
MAP_BASE_PATH  = 'ingre_nutrition_map'
os.makedirs(MAP_BASE_PATH, exist_ok=True)

EVAL_NUTRIENTS = {"Protein", "Carbohydrate", "Sugar", "Sodium", "Fat", "Saturated Fat", "Fiber","Fibre"}


def get_nutrientamount_foodcode(food_code):
    query_param = f'{REQ_NUT_AMOUNT}/?REQ_LANG={REQ_LANG}&id={food_code}'
    request_url = NUTRITION_BASE_URL + query_param
    response = requests.get(request_url)
    if response.status_code == 200:
        nutrient_data = response.json()
        return nutrient_data
    else:
        print(f"Failed to retrieve data for {food_code}: Status Code {response.status_code}")
        return None

def get_save_nutrient_to_file(ingre_match,ingre_name):
    
    food_code = ingre_match['food_code']
    map_data = get_nutrientamount_foodcode(food_code)
    

    if map_data:
        output_file_name = f"{MAP_BASE_PATH}/{food_code}_{ingre_name.replace(" ","_").replace('-', '_')}.json"
        aggregated_data = {
            "food_code": map_data[0]["food_code"],
            "ingredient_name": ingre_name,
            "description": ingre_match['description'],
            "nutrients": [
                eachNutri for eachNutri in map_data
                if any(eval_nutri.lower() in eachNutri["nutrient_web_name"].lower() for eval_nutri in EVAL_NUTRIENTS)
                ]
        }  
      
        with open(output_file_name, 'w') as f:
            json.dump(aggregated_data, f, indent=4)
        
        #print(f"Map data for {food_code} saved to {output_file_name}")
        return aggregated_data

    return False

def test_map_create():
    test_ingre = {
        "food_code": 6061,
        "description": "Test description"
    }
    get_save_nutrient_to_file(test_ingre,"Boneless rib-eye")


# test_map_create()

    
