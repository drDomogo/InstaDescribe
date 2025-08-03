import os
import openai
from pathlib import Path
import base64
import json

# Ustaw swój klucz OpenAI (lub użyj zmiennej środowiskowej)
openai.api_key = os.getenv("OPENAI_API_KEY")

# Ścieżka do folderu ze zdjęciami
IMAGE_FOLDER = "./photos"  # ← podmień na swoją ścieżkę

# Ścieżka do pliku z promptem
PROMPT_FILE = "prompt.json"

# Dozwolone rozszerzenia obrazów
VALID_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}

# Wczytaj prompt z pliku JSON
def load_prompt(prompt_path):
    with open(prompt_path, "r", encoding="utf-8") as f:
        return json.load(f)

# Funkcja: generowanie opisu zdjęcia z AI
def generate_caption_for_image(image_path, prompt_data):
    with open(image_path, "rb") as img_file:
        image_bytes = img_file.read()
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')

    # Zamień placeholder na base64 image url
    user_messages = prompt_data["user"]
    for msg in user_messages:
        if msg.get("type") == "image_url":
            msg["image_url"]["url"] = f"data:image/jpeg;base64,{image_base64}"

    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": prompt_data["system"]},
            {"role": "user", "content": user_messages}
        ],
        max_tokens=300
    )

    return response['choices'][0]['message']['content']

# Główna pętla: przetwarzanie obrazów
def process_images(folder_path, prompt_data):
    for image_file in Path(folder_path).iterdir():
        if image_file.suffix.lower() in VALID_EXTENSIONS:
            print(f"Przetwarzanie: {image_file.name}")
            try:
                caption = generate_caption_for_image(str(image_file), prompt_data)
                txt_file = image_file.with_suffix('.txt')
                with open(txt_file, 'w', encoding='utf-8') as f:
                    f.write(caption)
                print(f"✔️ Zapisano opis do: {txt_file.name}")
            except Exception as e:
                print(f"❌ Błąd przy {image_file.name}: {e}")

# Uruchomienie
if __name__ == "__main__":
    prompt_data = load_prompt(PROMPT_FILE)
    process_images(IMAGE_FOLDER, prompt_data)