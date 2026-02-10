# ==============================
# GST OCR SYSTEM - CONFIG
# Mobile-first | Stable
# ==============================

import os

# -------- MODE --------
# Options: BASIC | PRO | ELITE
MODE = os.environ.get("GST_MODE", "ELITE")

# -------- MODE CONFIG --------
MODE_CONFIG = {

    "BASIC": {
        "invoice_summary": True,
        "item_details": True,
        "tally_sales": False,
        "missing_correction": False,
        "dashboard": False,
        "confidence_score": False,
        "limit": 10
    },

    "PRO": {
        "invoice_summary": True,
        "item_details": True,
        "tally_sales": True,
        "missing_correction": True,
        "dashboard": False,
        "confidence_score": True,
        "limit": None
    },

    "ELITE": {   # FULL VERSION
        "invoice_summary": True,
        "item_details": True,
        "tally_sales": True,
        "missing_correction": True,
        "dashboard": True,
        "confidence_score": True,
        "limit": None
    }
}

# -------- SAFE ACCESS --------
def get_mode_config():
    return MODE_CONFIG.get(MODE, MODE_CONFIG["PRO"])
