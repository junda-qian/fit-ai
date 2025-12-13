"""
USDA FoodData Central API integration

This wrapper simplifies interaction with the USDA API.

USDA API Documentation: https://fdc.nal.usda.gov/api-guide.html

What this does:
1. Searches for foods by name (e.g., "banana", "chicken breast")
2. Parses the complex USDA response
3. Extracts only the data we need (calories, protein, carbs, fats)
4. Returns clean, simple results

Example:
    from food_database import food_db

    results = food_db.search_foods("banana")
    # Returns: List of bananas with nutrition info

Why we parse USDA data:
- USDA returns 150+ nutrients per food (vitamin A, B1, B2, iron, etc.)
- We only need 4 macros: calories, protein, carbs, fats
- This makes the data much simpler for the frontend
"""
import os
import requests
from typing import List, Optional
from dotenv import load_dotenv
from models import USDAFood, FoodSearchResult

# Load environment variables (USDA_API_KEY from .env file)
load_dotenv()

USDA_API_KEY = os.getenv("USDA_API_KEY")
USDA_BASE_URL = "https://api.nal.usda.gov/fdc/v1"


class FoodDatabase:
    """Wrapper for USDA FoodData Central API"""

    def __init__(self, api_key: str = USDA_API_KEY):
        """
        Initialize the food database wrapper

        Args:
            api_key: USDA API key (automatically loaded from .env)

        Raises:
            ValueError: If API key is not found
        """
        if not api_key:
            raise ValueError(
                "USDA_API_KEY not found! "
                "Please add it to backend/.env file: USDA_API_KEY=your-key-here"
            )
        self.api_key = api_key
        self.base_url = USDA_BASE_URL

    def search_foods(self, query: str, page_size: int = 10) -> FoodSearchResult:
        """
        Search for foods in USDA database

        Example:
            results = food_db.search_foods("banana", page_size=5)

            for food in results.foods:
                print(f"{food.description}: {food.calories} cal")
                print(f"  Protein: {food.protein}g")
                print(f"  Carbs: {food.carbs}g")
                print(f"  Fats: {food.fats}g")

        Args:
            query: Search term (e.g., "banana", "chicken breast")
            page_size: Number of results to return (default 10, max 50)

        Returns:
            FoodSearchResult with list of matching foods

        What happens:
        1. Calls USDA API with search query
        2. USDA returns foods with 150+ nutrients each
        3. We parse each food, extracting only calories/protein/carbs/fats
        4. Return simplified results
        """
        url = f"{self.base_url}/foods/search"

        # API request parameters
        params = {
            "api_key": self.api_key,
            "query": query,
            "pageSize": page_size,
            # Only search these high-quality databases:
            # - Survey (FNDDS): What Americans Actually Eat survey data
            # - Foundation: Core foods with detailed nutrient data
            # - SR Legacy: Standard Reference legacy database
            "dataType": ["Survey (FNDDS)", "Foundation", "SR Legacy"]
        }

        try:
            # Make API request
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()  # Raise error if request failed
            data = response.json()

            # Parse the results
            foods = []
            for food in data.get("foods", []):
                parsed_food = self._parse_food(food)
                if parsed_food:
                    foods.append(parsed_food)

            return FoodSearchResult(
                query=query,
                total_results=data.get("totalHits", 0),
                foods=foods
            )

        except requests.exceptions.RequestException as e:
            # If API call fails, return empty results
            print(f"USDA API error: {e}")
            return FoodSearchResult(query=query, total_results=0, foods=[])

    def _parse_food(self, food_data: dict) -> Optional[USDAFood]:
        """
        Parse USDA food data into our simple model

        USDA returns complex data like:
        {
          "fdcId": 173944,
          "description": "Bananas, raw",
          "foodNutrients": [
            {"nutrientId": 1008, "nutrientName": "Energy", "value": 89, "unitName": "KCAL"},
            {"nutrientId": 1003, "nutrientName": "Protein", "value": 1.09, "unitName": "G"},
            {"nutrientId": 1005, "nutrientName": "Carbohydrate", "value": 22.84, "unitName": "G"},
            {"nutrientId": 1004, "nutrientName": "Total lipid (fat)", "value": 0.33, "unitName": "G"},
            ... 150+ more nutrients ...
          ]
        }

        We simplify it to:
        {
          "fdc_id": 173944,
          "description": "Bananas, raw",
          "calories": 89,
          "protein": 1.09,
          "carbs": 22.84,
          "fats": 0.33,
          "serving_size": "100",
          "serving_unit": "g"
        }

        Args:
            food_data: Raw food data from USDA API

        Returns:
            Simplified USDAFood object or None if parsing fails
        """
        try:
            # Extract basic info
            fdc_id = food_data.get("fdcId")
            description = food_data.get("description", "Unknown Food")

            # Extract nutrients array
            nutrients = food_data.get("foodNutrients", [])

            # Create a map of nutrient ID -> value for easy lookup
            # This makes it easy to find specific nutrients
            nutrient_map = {}
            for nutrient in nutrients:
                nutrient_id = nutrient.get("nutrientId")
                value = nutrient.get("value", 0)
                nutrient_map[nutrient_id] = value

            # USDA Nutrient IDs (these are standardized across all foods):
            # 1008 = Energy (calories) in kcal
            # 1003 = Protein in grams
            # 1005 = Carbohydrate in grams
            # 1004 = Total Fat in grams
            #
            # Note: These IDs are the same for ALL foods in USDA database
            # So "1008" always means calories, whether it's a banana or steak

            calories = nutrient_map.get(1008, 0)
            protein = nutrient_map.get(1003, 0)
            carbs = nutrient_map.get(1005, 0)
            fats = nutrient_map.get(1004, 0)

            # Get serving size (defaults to 100g if not specified)
            # Most USDA data is per 100g, which is convenient
            serving_size = food_data.get("servingSize", 100)
            serving_unit = food_data.get("servingSizeUnit", "g")

            return USDAFood(
                fdc_id=fdc_id,
                description=description,
                calories=round(calories, 1),
                protein=round(protein, 1),
                carbs=round(carbs, 1),
                fats=round(fats, 1),
                serving_size=str(serving_size),
                serving_unit=serving_unit
            )

        except Exception as e:
            # If parsing fails for this food, skip it
            # This prevents one bad food from breaking the entire search
            print(f"Error parsing food: {e}")
            return None


# Global instance - import and use this
# Usage: from food_database import food_db
food_db = FoodDatabase()
