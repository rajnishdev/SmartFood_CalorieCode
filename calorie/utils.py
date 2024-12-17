import os
import requests

def fetch_nutrition(meal_name):
    # Replace with a real API key and endpoint
    API_URL = "https://api.edamam.com/api/nutrition-data"
    API_APP_ID = os.environ.get("API_APP_ID")
    API_APP_KEY = os.environ.get("API_APP_KEY")

    params = {
        "app_id": API_APP_ID,
        "app_key": API_APP_KEY,
        "ingr": meal_name
    }

    response = requests.get(API_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        return {
            "calories": data.get("calories", 0),
            "protein": data.get("totalNutrients", {}).get("PROCNT", {}).get("quantity", 0),
            "carbs": data.get("totalNutrients", {}).get("CHOCDF", {}).get("quantity", 0),
            "fats": data.get("totalNutrients", {}).get("FAT", {}).get("quantity", 0),
        }
    return {"calories": 0, "protein": 0, "carbs": 0, "fats": 0}
