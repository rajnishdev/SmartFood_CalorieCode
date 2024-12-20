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
            "cholestrol": data.get("totalNutrients", {}).get("CHOLE", {}).get("quantity", 0),
            "iron": data.get("totalNutrients", {}).get("FE", {}).get("quantity", 0),
            "calcium": data.get("totalNutrients", {}).get("CA", {}).get("quantity", 0),
            "sodium": data.get("totalNutrients", {}).get("NA", {}).get("quantity", 0),
            "magnesium": data.get("totalNutrients", {}).get("MG", {}).get("quantity", 0),
            "phosphorus": data.get("totalNutrients", {}).get("P", {}).get("quantity", 0),
            "zinc": data.get("totalNutrients", {}).get("ZN", {}).get("quantity", 0),
            "vitaminb12": data.get("totalNutrients", {}).get("VITB12", {}).get("quantity", 0),
            "folic_acid": data.get("totalNutrients", {}).get("FOLAC", {}).get("quantity", 0),
        }
    return {"calories": 0, "protein": 0, "carbs": 0, "fats": 0,"cholestrol":0, "iron":0, "calcium":0, "sodium":0, "magnesium":0, "phosphorus":0,"zinc":0, "vitaminb12":0 ,"folic_acid":0}
