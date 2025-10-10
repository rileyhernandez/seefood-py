import base64
import time
from pathlib import Path
from openai import OpenAI

# system_prompt = """
#     You are a quality tool for a restaurant to determine whether or not all ordered items are present in each order, and whether they each contain their respective ingredients.
#     I will present you a picture and list of all items that should be present in this order along with each item's ingredients.
#     Here are our ingredients:
#
#     Order Items:
#     Shrimp Bowl (white sushi rice, shrimp, broccoli),
#     Lay's Potato Chips,
#     BBQ Sauce Packet
#
#     For each item in the list, I want you to return whether or not it is present, and if it has ingredients, return if it's ingredients are present in the following way.
#     You should respond only with a valid array of json objects.
#     Each json object in the array should represent an item in the item list.
#     Each item json should have the field "name" with a value of a string of the item's name and a field called "present" with a boolean value of it is present in the picture.
#     If i provided ingredients for the item, there should also be a field called "ingredients" and that should be an array of the ingredients i provided, each with a "name" field for their
#     name and and "present" field with a boolean of its presence.
#     For items with ingredients, only consider the ingredient present if it is in that item. Not if it is present somewhere else in the picture.
#     Respond only with a valid JSON, no extra text or code fences.
#
#     """

system_prompt = """
    You are a quality tool for a restaurant to determine whether or not all ordered items are present in each order, and whether they each contain their respective ingredients.
    I will present you a picture and list of all items that should be present in this order along with each item's ingredients.
    Here are our ingredients:

    Order Items:
    Hawaiian Ahi Bowl (Ahi tuna, Edamame, Seaweed salad, Sesame seeds, White rice, Avocado, Pickled Ginger)
    
    By the way, if there is a bowl in the image, assume there is always Ahi tuna present.
    For each item in the list, I want you to return whether or not it is present, and if it has ingredients, return if it's ingredients are present in the following way.
    You should respond only with a valid array of json objects.
    Each json object in the array should represent an item in the item list. 
    Each item json should have the field "name" with a value of a string of the item's name and a field called "present" with a boolean value of it is present in the picture.
    If i provided ingredients for the item (indicated by parentheses following the item, only consider ingredients if i have them listed in parentheses!), there should also be a field called "ingredients" and that should be an array of the ingredients i provided, each with a "name" field for their
    name and and "present" field with a boolean of its presence.
    For items with ingredients, only consider the ingredient present if it is in that item. Not if it is present somewhere else in the picture.
    Respond only with a valid JSON, no extra text or code fences.
    If nothing is present, make sure to still give the JSON just with the items as false in the present field.

    """


class OpenAiConvo:
    client: OpenAI
    model: str
    system_prompt: str

    def __init__(self, system_prompt: str = system_prompt,  model: str = "gpt-4o-mini"):
        client = OpenAI()
        self.client = client
        self.model = model
        self.system_prompt = system_prompt

    def _encode_image(self, image_path: Path) -> str:
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    def prompt(self, image_path: Path, notes: str = "Analyze this meal.") -> str:
        image_b64 = self._encode_image(image_path)

        start = time.time()
        response = self.client.responses.create(
            model=self.model,
            input=[
                {
                    "role": "system",
                    "content": self.system_prompt,
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": notes},
                        {"type": "input_image", "image_url": f"data:image/jpeg;base64,{image_b64}"},
                    ],
                },
            ],
        )

        end = time.time()
        print(f"Query Time: {end - start:.2f}s")
        return response.output_text


# Preload the image once (optional, if it's static)
image_path = Path(__file__).parent.parent.parent / ".images" / "test.jpg"

if __name__ == "__main__":
    image_path = Path(__file__).parent.parent.parent / ".images" / "test.jpg"
    open_ai_convo = OpenAiConvo(image_path=image_path)

    while True:
        user_input = input("Press Enter to analyze or 'q' to quit: ").strip().lower()
        if user_input == "q":
            break

        response = open_ai_convo.prompt()
        print("--- Response: ---")
        print(response)
        print("-------------------")
