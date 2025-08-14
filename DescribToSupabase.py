import os
import openai
import uuid
from pathlib import Path
import base64
import json
from supabase import create_client

# ---------------- Konfiguracja ----------------
openai.api_key = os.getenv("OPENAI_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

IMAGE_FOLDER = "./photos"  # folder z lokalnymi zdjęciami
PROMPT_FILE = "prompt.json"  # plik z promptem dla AI
VALID_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


# ---------------- Funkcje ----------------
def load_prompt(prompt_path):
    with open(prompt_path, "r", encoding="utf-8") as f:
        return json.load(f)


def generate_caption_for_image(image_path, prompt_data):
    with open(image_path, "rb") as img_file:
        image_bytes = img_file.read()
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')

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


def upload_image_to_supabase(local_file_path):
    """Wrzuć zdjęcie do bucket 'photos' z unikalną nazwą UUID"""
    file_name = f"{uuid.uuid4()}_{os.path.basename(local_file_path)}"
    with open(local_file_path, "rb") as f:
        result = supabase.storage.from_("photos").upload(file_name, f)

    print("\n=== DEBUG: upload() result ===")
    print(f"Typ obiektu: {type(result)}")
    print(f"Atrybuty: {dir(result)}")
    print(f"Cały obiekt: {result}")
    print("==============================\n")

    public_url = supabase.storage.from_("photos").get_public_url(file_name)
    return file_name, public_url


def insert_description_to_db(photo_name, description_text):
    """Dodaj wiersz do tabeli 'descriptions'"""
    result = supabase.table("descriptions").insert({
        "photo": photo_name,
        "description": description_text
    }).execute()
    print(f"📄 Insert result: {result.data}")
    return result


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

                photo_name, public_url = upload_image_to_supabase(str(image_file))
                insert_description_to_db(photo_name, caption)
                print(f"📤 Wysłano do Supabase. Publiczny URL: {public_url}\n")

            except Exception as e:
                print(f"❌ Błąd przy {image_file.name}: {e}")


# ---------------- Uruchomienie ----------------
if __name__ == "__main__":
    prompt_data = load_prompt(PROMPT_FILE)
    process_images(IMAGE_FOLDER, prompt_data)
