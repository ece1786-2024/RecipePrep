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

def get_save_nutrient_to_file(food_code):
    
    output_file_name = f"{MAP_BASE_PATH}/{food_code}.json"
    
    map_data = get_nutrientamount_foodcode(food_code)
    
    if map_data:
        with open(output_file_name, 'w') as f:
            json.dump(map_data, f, indent=4)
        
        print(f"Map data for {food_code} saved to {output_file_name}")
        return True

    return False

def test_map_create():
    get_save_nutrient_to_file(6061)

#test_map_create()

    
