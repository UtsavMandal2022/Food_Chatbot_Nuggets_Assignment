import requests
from bs4 import BeautifulSoup
import csv
import time
import random

FOOD_SITES = [
    "https://www.allrecipes.com/recipes/",
    "https://www.foodnetwork.com/recipes"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def scrape_recipe(url):
    response = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    data = {
        'id': random.randint(1000, 9999),
        'name': soup.find('h1').text.strip(),
        'ingredients': str([li.text.strip() for li in soup.select('ul.ingredients-list li')]),
        'ingredients_count': len(soup.select('ul.ingredients-list li')),
        'user_id': random.randint(100000, 999999),
        'rating': round(float(soup.find('meta', {'itemprop':'ratingValue'})['content']), 1),
        'review': ' '.join([p.text.strip() for p in soup.select('div.review-text')]),
        'calories': soup.find('span', class_='calories').text.strip() if soup.find('span', class_='calories') else 'N/A'
    }
    
    return data

def main():
    with open('scraped_food_data.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['id', 'name', 'ingredients', 'ingredients_count', 
                     'user_id', 'rating', 'review', 'calories']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        # Scrape 50 recipes as sample data
        recipe_urls = [
            "https://www.allrecipes.com/recipe/17481/simple-white-cake/",
            "https://www.foodnetwork.com/recipes/food-network-kitchen/vanilla-cake-recipe-2120254",
            "https://www.allrecipes.com/recipe/17481/simple-white-cake/", "https://www.allrecipes.com/recipe/277000/easy-vanilla-cake/", "https://www.allrecipes.com/recipe/17981/one-bowl-chocolate-cake-iii/", "https://www.allrecipes.com/recipe/7399/tres-leches-milk-cake/", "https://www.bbcgoodfood.com/recipes/courgette-lemon-thyme-cake", "https://www.bbcgoodfood.com/recipes/brazilian-carrot-cake", "https://www.bbcgoodfood.com/recipes/chocolate-chip-pecan-butternut-bread"
        ]
        
        for url in recipe_urls:
            try:
                recipe_data = scrape_recipe(url)
                writer.writerow(recipe_data)
                time.sleep(random.uniform(1, 3))  # Respect crawl delay
            except Exception as e:
                print(f"Error scraping {url}: {str(e)}")

if __name__ == "__main__":
    main()