import os
import boto3
import json
import hashlib
import time
from datetime import datetime

# ---------------- CONFIG ----------------
INPUT_DIR = "input_invoices"
TEXTRACT_DIR = "textract_json"  #
PROCESSED_LOG = "processed_files.json"

# AWS Credentials (VoltAgent will use these)
# सुनिश्चित करें कि आपके सिस्टम में AWS CLI कॉन्फ़िगर है या .env फाइल है
textract = boto3.client('textract', region_name='us-east-1')

os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(TEXTRACT_DIR, exist_ok=True)

def get_file_hash(file_path):
    """फाइल का यूनिक सिग्नेचर बनाती है ताकि दोबारा बिल न बने।"""
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

def load_log():
    if os.path.exists(PROCESSED_LOG):
        with open(PROCESSED_LOG, 'r') as f:
            return json.load(f)
    return {}

def save_log(log_data):
    with open(PROCESSED_LOG, 'w') as f:
        json.dump(log_data, f, indent=4)

def upload_to_textract(file_path):
    """AWS Textract Synchronous API का उपयोग (Single page documents के लिए सस्ता)"""
    with open(file_path, 'rb') as document:
        image_bytes = document.read()

    try:
        response = textract.detect_document_text(Document={'Bytes': image_bytes})
        return response
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return None

def sync_and_process():
    processed_log = load_log()
    current_files = os.listdir(INPUT_DIR)
    
    print(f"🚀 Scanning {INPUT_DIR}...")
    
    for filename in current_files:
        if not filename.lower().endswith(('.pdf', '.jpg', '.jpeg', '.png')):
            continue
            
        file_path = os.path.join(INPUT_DIR, filename)
        file_hash = get_file_hash(file_path)
        
        # COST CONTROL: क्या यह फाइल पहले प्रोसेस हो चुकी है?
        if file_hash in processed_log:
            print(f"⏩ Skipping {filename} (Already processed to save cost)")
            continue
            
        print(f"⏳ Calling AWS Textract for: {filename}...")
        result = upload_to_textract(file_path)
        
        if result:
            json_filename = f"{os.path.splitext(filename)[0]}.json"
            output_path = os.path.join(TEXTRACT_DIR, json_filename)
            
            with open(output_path, 'w') as f:
                json.dump(result, f)
            
            # लॉग में एंट्री करें
            processed_log[file_hash] = {
                "filename": filename,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            save_log(processed_log)
            print(f"✅ Saved JSON to {output_path}")

if __name__ == "__main__":
    sync_and_process()

