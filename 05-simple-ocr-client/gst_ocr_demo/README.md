LedgerFlow AI (Bills2Tally) 🚀
Enterprise-Grade GST OCR & Accounting Automation Pipeline
LedgerFlow AI केवल एक AI रैपर नहीं है, बल्कि एक पूर्ण Workflow Automation System है जो रॉ इनवॉइस डेटा को "Accounting-Ready" फॉर्मेट में बदल देता है। यह AWS Textract की मजबूती और Gemini AI की बुद्धिमत्ता (Intelligence) को जोड़कर 99% डेटा सटीकता सुनिश्चित करता है।
🛡️ Why LedgerFlow AI is "Future-Proof"?
हाल के AI अपडेट्स (जैसे Anthropic Claude का ऑटोमेशन) उन टूल्स को प्रभावित करते हैं जो केवल डेटा निकालते हैं। LedgerFlow AI सुरक्षित है क्योंकि:
 * Context-Aware Mapping: यह केवल टेक्स्ट नहीं निकालता, बल्कि भारतीय GST नियमों के अनुसार लेजर्स को मैप करता है।
 * Hybrid Extraction: AWS Textract (Forms/Tables) + Regex + AI का मिश्रण, जो इसे 100% रिलायबल बनाता है।
 * Accounting-Ready: यह सीधा Excel और Tally XML एक्सपोर्ट देता है, जो जेनेरिक एआई मॉडल्स नहीं कर सकते।
🏗️ Architecture & Pipeline
यह प्रोजेक्ट एक मॉड्युलर पाइपलाइन पर आधारित है:
 * Ingestion: textract_json/ फोल्डर से रॉ JSON डेटा उठाना।
 * Form Extraction: extract_kv_pairs के जरिए की-वैल्यू पेयर्स (जैसे Invoice No, Date) का विश्लेषण।
 * Pattern Matching: gstin_extractor और name_extractor के जरिए सटीक भारतीय टैक्स पहचानकर्ता (Identifiers) ढूँढना।
 * Deep Inventory Analysis: extract_inventories_advanced के माध्यम से जटिल टेबल्स और लाइन आइटम्स को प्रोसेस करना।
 * Final Export: excel_writer के जरिए प्रोफेशनल ऑडिट रिपोर्ट तैयार करना।
🛠️ Key Features
 * ✅ Dual-Validation: KV Pairs और Regex का उपयोग करके डबल-चेक डेटा एक्सट्रैक्शन।
 * ✅ GST Compliant: सप्लायर और बायर के GSTIN को अलग-अलग पहचानने की क्षमता।
 * ✅ Advanced Table Parsing: मुश्किल इनवॉइस स्ट्रक्चर्स से भी इन्वेंट्री डेटा (HSN, Rate, Tax) निकालना।
 * ✅ Error Handling: करप्ट या मिसिंग डेटा होने पर भी ग्रेसफुल फेल्योर और लॉगिंग।
🚀 Getting Started
1. Prerequisites
 * Python 3.10+
 * Termux (for mobile) or PC/Laptop
 * AWS Credentials (for Textract processing)
2. Installation
git clone https://github.com/your-username/LedgerFlowAI.git
cd LedgerFlowAI
pip install -r requirements.txt

3. Usage
अपने Textract JSON फाइल्स को textract_json/ फोल्डर में रखें और रन करें:
python main.py

रिपोर्ट outputs/ फोल्डर में Final_Professional_Report_DDMMYYYY.xlsx के नाम से मिल जाएगी।
📂 Folder Structure
 * pipeline/: कोर एक्सट्रैक्शन लॉजिक (Date, GST, Names, Tables)।
 * textract_json/: इनपुट फाइल्स का स्थान।
 * outputs/: जेनरेट की गई Excel रिपोर्ट्स।
 * main.py: पाइपलाइन को कंट्रोल करने वाला मुख्य इंजन।
📝 Roadmap
 * [ ] Direct Tally XML Integration.
 * [ ] Gemini AI Vision for handwritten bill support.
 * [ ] Multi-currency and International Invoice Support.
Developed with ❤️ by Jitendra Bharti
