from nltk.stem import WordNetLemmatizer
import re
import os
import requests
import json
import faiss


#From CNF API
FOOD_CODE_URL = "https://food-nutrition.canada.ca/api/canadian-nutrient-file/food/?lang=en&type=json"
FOOD_CODE_FILENAME = 'CNF_API_food_code.json'

DATASET_PATH = './datasets'
EMB_PATH =  './datasets/emb'
FOOD_DES_FAISS_INDEX_NAME = 'food_index.faiss'
os.makedirs(EMB_PATH, exist_ok=True)


lemmatizer = WordNetLemmatizer()


#Load Ingredient food_code dataset
def get_food_code_dataset():
    res = requests.get(FOOD_CODE_URL)
    food_code_data = res.json()
    food_code_filename = FOOD_CODE_FILENAME
    file_name_food_code = f"{DATASET_PATH}/{food_code_filename}"
    with open(file_name_food_code, "w") as f:
        json.dump(food_code_data, f, indent=4)
    
    return food_code_data

def preprocess_text(text):
    # Lowercase and remove punctuation
    text = text.strip().lower()
    text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation

    text = " ".join([lemmatizer.lemmatize(word) for word in text.split()])
    
    return text

def get_normalized_foodCode_dataset():
    with open( os.path.join(DATASET_PATH,FOOD_CODE_FILENAME), "r") as file:
        food_code_dataset = json.load(file)

    #Clean the description
    food_descriptions = [
        f"{preprocess_text(item['food_description'])}" 
        for item in food_code_dataset
    ]
    food_codes = [item["food_code"] for item in food_code_dataset]
    
    return food_descriptions,food_codes

def get_regular_foodCode_dataset():
    with open( os.path.join(DATASET_PATH,FOOD_CODE_FILENAME), "r") as file:
        food_code_dataset = json.load(file)

    #Clean the description
    food_descriptions = [
        f"{item['food_description']}" 
        for item in food_code_dataset
    ]
    food_codes = [item["food_code"] for item in food_code_dataset]
    return food_descriptions,food_codes
    

def create_FAISS_Index(food_embeddings):
    # Create a FAISS index
    dimension = food_embeddings.shape[1]  # Embedding dimension
    index = faiss.IndexFlatL2(dimension)
    index.add(food_embeddings)  # Add embeddings to the index

    # Save the FAISS index for future use
    faiss_idx_path = os.path.join(EMB_PATH,FOOD_DES_FAISS_INDEX_NAME)
    faiss.write_index(index, faiss_idx_path)
    print(f"FAISS index saved in {faiss_idx_path}")
    
    return index