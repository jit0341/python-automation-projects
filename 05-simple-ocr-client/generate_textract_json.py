import boto3
import json
import os

textract = boto3.client("textract", region_name="ap-south-1")

INPUT_DIR = "input"
OUTPUT_DIR = "textract_json"

os.makedirs(OUTPUT_DIR, exist_ok=True)

def process_image(file_path, out_json):
    with open(file_path, "rb") as f:
        image_bytes = f.read()

    response = textract.analyze_document(
        Document={"Bytes": image_bytes},
        FeatureTypes=["FORMS", "TABLES"]
    )

    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(response, f, indent=2)

def process_pdf(file_path, out_json):
    # SIMPLE MODE: sync only works for images
    # PDF ke liye async hota hai (next step me batata hoon)
    raise NotImplementedError("PDF async Textract next step")

for file in os.listdir(INPUT_DIR):
    in_path = os.path.join(INPUT_DIR, file)
    out_path = os.path.join(OUTPUT_DIR, file + ".json")

    if file.lower().endswith((".jpg", ".jpeg", ".png")):
        print("Processing image:", file)
        process_image(in_path, out_path)

    elif file.lower().endswith(".pdf"):
        print("Skipping PDF for now:", file)
