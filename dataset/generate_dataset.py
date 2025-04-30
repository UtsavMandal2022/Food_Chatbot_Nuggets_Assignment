import json
import pandas as pd
import sys
import os

# Add the parent directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Now you can import the config module
import config

# Setup project paths
base_folder = 'D:/Projects/datatalks-final-project/'
input_data_folder = base_folder + 'dataset/'

# Read menu items from CSV
menu_items_df = pd.read_csv(config.dataset_folder+'scraped_food_data.csv')

# Read questions from JSON file
with open(config.dataset_folder+'user_questions.json', 'r') as f:
    questions = json.load(f)

# Convert DataFrame to list of dictionaries (each representing a menu item)
menu_items = menu_items_df.to_dict(orient='records')

# Function to create a single entry based on a menu item
def create_entry(menu_item):
    documents = []
    for q in questions:
        field_value = menu_item.get(q['field'], "N/A")
        
        # Customize the text based on the section and question
        if q['section'] == 'ingredients':
            text = f"The {menu_item['name']} contains the following ingredients: {', '.join(field_value.split(', ')) if isinstance(field_value, str) else field_value}"
        elif q['section'] == 'calories':
            text = f"The {menu_item['name']} has {field_value} calories."
        elif q['section'] == 'nutritional':
            text = f"The {menu_item['name']} has {field_value} grams of {q['field'].replace('_', ' ')}."
        elif q['section'] == 'preparation':
            text = f"The {menu_item['name']} takes {field_value} minutes to prepare."
        elif q['section'] == 'rating':
            text = f"The {menu_item['name']} has a rating of {field_value}."
        elif q['section'] == 'review':
            text = f"Review for {menu_item['name']}: {field_value}"
        elif q['section'] == 'calorie_status':
            text = f"The calorie status of {menu_item['name']} is {field_value}."
        elif q['section'] == 'price':
            text = f"The price of {menu_item['name']} is ${field_value}."
        else:
            text = f"The {menu_item['name']} contains {field_value}"

        documents.append({
            "id": f"{menu_item['id']}_{q['field_id']}",
            "question": q["question"],
            "section": q["section"],
            "text": text
        })
    return {
        "dish name": menu_item['name'],
        "documents": documents
    }

# Generate the dataset for all menu items
data = []
for item in menu_items:
    data.append(create_entry(item))

# Create the final structure with the category key
final_data = {
    "category": "menu items",
    "dishes": data
}

# Write to JSON file
with open(config.dataset_folder+'main_faq_database.json', 'w') as f:  # Adjust filename as needed
    json.dump(final_data, f, indent=2)