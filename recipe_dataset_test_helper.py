import json
import random

#Get N random testing examples 
sample_size = 100
output_file_name = 'sampled_test_data.json'

with open("recipes_raw/recipes_raw_nosource_fn.json", "r") as f:
    data = json.load(f)

sampled_items = random.sample(list(data.items()), sample_size)
sampled_data = dict(sampled_items)

with open(output_file_name, "w") as f:
    json.dump(sampled_data, f, indent=4)

print(f"{sample_size} records have been saved to {output_file_name}.")