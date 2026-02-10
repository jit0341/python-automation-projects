import os

import json

import boto3



SUPPORTED_EXT = (".pdf", ".png", ".jpg", ".jpeg")



def run_textract_on_input(input_dir="input", output_dir="textract_json"):

    os.makedirs(output_dir, exist_ok=True)



    textract = boto3.client("textract", region_name="ap-south-1")



    for fname in os.listdir(input_dir):

        if not fname.lower().endswith(SUPPORTED_EXT):

            continue



        input_path = os.path.join(input_dir, fname)

        output_path = os.path.join(output_dir, fname + ".json")



        if os.path.exists(output_path):

            continue  # already processed



        print(f"🔍 OCR running on: {fname}")



        with open(input_path, "rb") as f:

            bytes_data = f.read()



        response = textract.analyze_document(

            Document={"Bytes": bytes_data},

            FeatureTypes=["TABLES", "FORMS"]

        )



        with open(output_path, "w", encoding="utf-8") as out:

            json.dump(response, out)



        print(f"✅ JSON generated: {output_path}")

