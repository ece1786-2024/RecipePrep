import requests
import json
import os
import random

# Canadian Nutrient (CNF) API endpoints
#https://produits-sante.canada.ca/api/documentation/cnf-documentation-en.html#a6
NUTRITION_BASE_URL = 'https://food-nutrition.canada.ca'
REQ_LANG='en'
REQ_NUT_AMOUNT = '/api/canadian-nutrient-file/nutrientamount'
REQ_NUT_NAME = '/api/canadian-nutrient-file/nutrientname'
#For output
MAP_BASE_PATH  = './ingre_nutrition_map'
NUT_UNIT_MAP_NAME = 'nutrient_unit_map.json'
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

def get_nutrientname_foodcode(nut_name_id):
    query_param = f'{REQ_NUT_NAME}/?REQ_LANG={REQ_LANG}&id={nut_name_id}'
    request_url = NUTRITION_BASE_URL + query_param
    response = requests.get(request_url)
    if response.status_code == 200:
        nutrient_data = response.json()
        #print(nutrient_data)
        return nutrient_data
    else:
        print(f"Failed to retrieve data for nutrient_nameId {nut_name_id}: Status Code {response.status_code}")
        return None

def get_save_nutrient_to_file(ingre_match,ingre_name,nutri_id_map):
    
    food_code = ingre_match['food_code']
    map_data = get_nutrientamount_foodcode(food_code)
    

    if map_data:
        nutrients = []
        for eachNutri in map_data:
            # Check if the nutrient should be included
            if any(eval_nutri.lower() in eachNutri["nutrient_web_name"].lower() for eval_nutri in EVAL_NUTRIENTS):
                nut_id = str(eachNutri["nutrient_name_id"])
                
                if nut_id in nutri_id_map:
                    nutri_unit = nutri_id_map[nut_id]
                else:
                    nutri_unit = get_nutrientname_foodcode(nut_id)
                    nutri_unit  = 'g' if nutri_unit==None else nutri_unit["unit"]                   
                    nutri_id_map[nut_id] =  nutri_unit
               
                nutrient_info = {
                    "food_code": eachNutri["food_code"],
                    "nutrient_value": eachNutri["nutrient_value"],
                    #"nutrient_name_id": eachNutri["nutrient_name_id"],
                    "nutrient_web_name": eachNutri["nutrient_web_name"],
                    "unit": nutri_unit  # Get the unit from function
                }
                nutrients.append(nutrient_info)
        aggregated_data = {
            "ingredient_name": ingre_name,
            "nutrients": nutrients
        }
      
        # #Uncomment below to save result to a file
        # output_file_name = f"{MAP_BASE_PATH}/{food_code}_{ingre_name.replace(" ","_").replace('-', '_')}.json"
        # with open(output_file_name, 'w') as f:
        #     json.dump(aggregated_data, f, indent=4)
        # #print(f"Map data for {food_code} saved to {output_file_name}")
        return aggregated_data,nutri_id_map

    return False

def load_nut_id_map(unit_map_name):
    if os.path.exists(unit_map_name):
        with open(unit_map_name, 'r') as f:
            return json.load(f)
    else:
        return {}
    
def save_nut_id_map(nut_id_map,unit_map_name):
    with open(unit_map_name, 'w') as f:
        json.dump(nut_id_map, f, indent=4)
    
    print(f"Unit map {unit_map_name} updated!")
    
'''Small Helpers'''
def count_items_in_dataset(file_path):
    with open(file_path, "r") as file:
        dataset = json.load(file)
    return len(dataset) 

def save_N_random_items(in_filename, out_filename, N):

    # Load the dataset
    with open(in_filename, "r") as f:
        data = json.load(f)
    
    # Select N random items
    if N > len(data):
        print(f"Requested {N} items, but the dataset contains only {len(data)} items. Selecting all items.")
        N = len(data)
        
    random_items = random.sample(data, N)

    # Save the selected items to a new file
    with open(out_filename, "w") as f:
        json.dump(random_items, f, indent=4)
    
    print(f"{N} random items have been saved to {out_filename}.")


'''
    For testing
'''

def get_unitMap_name():
    return  f"{MAP_BASE_PATH}/{NUT_UNIT_MAP_NAME}"
    
def test_map_create():
    test_ingre = {
        "food_code": 6061,
        "description": "Test description"
    }
    unit_map_name =get_unitMap_name()
    untri_unit_map = load_nut_id_map(unit_map_name)
    
    aggregated_data,nutri_unit_map_ret= get_save_nutrient_to_file(test_ingre,"Boneless rib-eye",untri_unit_map)
   
    save_nut_id_map(nutri_unit_map_ret,unit_map_name)


def test_mapping_size():
    # Example usage
    file_path = "./datasets/CNF_API_food_code.json"  # Path to your dataset_2 file
    num_items = count_items_in_dataset(file_path)
    print(f"The dataset contains {num_items} items.")

def get_smaller_map():
    file_path = "./datasets/CNF_API_food_code.json"  
    out_file = "./datasets/CNF_API_food_code_test.json"  
    N=1000
    save_N_random_items(file_path,out_file,N)

# get_smaller_map()

    
