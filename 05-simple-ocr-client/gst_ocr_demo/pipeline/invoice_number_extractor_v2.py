import re
from difflib import SequenceMatcher

# ============================================================
# 🔒 ENHANCED KEYWORD CANON
# ============================================================

INVOICE_KEYS = [
    "invoice no", "invoice number", "inv no", "inv. no", "invoice#",
    "inv#", "invoice#", "tax invoice no", "tax invoice number",
    "bill no", "bill number", "bill#", "bill no.",
    "document no", "doc no", "invoice ref", "ref no",
    "voucher no", "voucher number", "receipt no"
]

# ============================================================
# 🔒 ENHANCED REGEX PATTERNS (Priority Ordered)
# ============================================================

REGEX_PATTERNS = [
    # Explicit invoice label with colon/dash
    r"(?i)invoice(?:\s*number|\s*no|\.?\s*no)?\s*[:\-]\s*([A-Z0-9][A-Z0-9\/\-\#]{2,80})",
    
    # Tax invoice explicit
    r"(?i)tax\s+invoice\s*(?:no|number|\#)?\s*[:\-]?\s*([A-Z0-9][A-Z0-9\/\-\#]{2,80})",
    
    # Bill No variants
    r"(?i)bill(?:\s*no|\.?\s*no|number|\#)?\s*[:\-]\s*([A-Z0-9][A-Z0-9\/\-\#]{2,80})",
    
    # INV prefix variants
    r"(?i)\bINV(?:OICE)?[\s\-\#:]{0,3}([A-Z0-9][A-Z0-9\/\-\#]{2,80})\b",
    
    # Document/Voucher number
    r"(?i)(?:doc|voucher)(?:\s*no|\.?\s*no)?\s*[:\-]\s*([A-Z0-9][A-Z0-9\/\-\#]{2,80})",
    
    # Pattern-only fallback (high recall)
    r"\b([A-Z]{2,5}[\-\/]?\d{3,8}[\-\/]?[A-Z0-9]{0,8})\b"
]

# ============================================================
# ❌ HARD REJECT PATTERNS
# ============================================================

DATE_RE = r"\b(\d{2}[\/\-]\d{2}[\/\-]\d{2,4}|\d{4}[\/\-]\d{2}[\/\-]\d{2})\b"
GSTIN_RE = r"\b\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z\d]{1}Z[A-Z\d]\b"
VEHICLE_RE = r"^[A-Z]{2}\d{2}[A-Z]{1,2}\d{3,4}$"
AMOUNT_RE = r"[₹\u20B9]\s*\d+(\.\d{2})?"
PHONE_RE = r"\b\d{10}\b"
PINCODE_RE = r"\b\d{6}\b"

BAD_TOKENS = {
    "invoice", "tax invoice", "signature", "authorised", "authorized",
    "gst invoice", "bill", "total", "subtotal", "grand total",
    "page", "copy", "original", "duplicate", "triplicate"
}

# ============================================================
# ✅ ENHANCED TOKEN VALIDATOR
# ============================================================

def is_valid_invoice_number(token: str) -> bool:
    """Enhanced validation with multiple checks"""
    t = token.lower().strip()
    
    # Check bad tokens
    if t in BAD_TOKENS:
        return False
    
    # Check GSTIN pattern
    if re.fullmatch(GSTIN_RE, token):
        return False
    
    # Must have at least one digit
    if not any(ch.isdigit() for ch in t):
        return False
    
    # Must have at least one letter OR be a pure number > 100
    has_letter = any(ch.isalpha() for ch in t)
    if not has_letter:
        try:
            num = int(re.sub(r'[^\d]', '', token))
            if num < 100:  # Too small to be invoice number
                return False
        except:
            return False
    
    # Length check
    if len(t) < 3 or len(t) > 50:
        return False
    
    # File extension check
    if t.endswith((".jpg", ".png", ".pdf", ".json")):
        return False
    
    # Phone number check
    if re.fullmatch(PHONE_RE, token):
        return False
    
    # Pincode check
    if re.fullmatch(PINCODE_RE, token):
        return False
    
    return True

# ============================================================
# 🎯 FUZZY MATCHING FOR KEYWORDS
# ============================================================

def fuzzy_match_keyword(text: str, threshold: float = 0.8) -> bool:
    """Check if text fuzzy matches any invoice keyword"""
    text_lower = text.lower()
    for keyword in INVOICE_KEYS:
        ratio = SequenceMatcher(None, text_lower, keyword).ratio()
        if ratio >= threshold:
            return True
    return False

# ============================================================
# 🧠 ENHANCED CORE EXTRACTOR
# ============================================================

def extract_invoice_number(textract_lines):
    """
    Enhanced invoice number extraction with:
    - Better pattern matching
    - Fuzzy keyword matching
    - Multi-pass extraction
    - Improved confidence scoring
    """
    candidates = []
    debug_rows = []
    
    # Pass 1: Pattern-based extraction
    for idx, item in enumerate(textract_lines):
        text = (item.get("text") or "").strip()
        confidence = item.get("confidence", 0)
        source = item.get("source", "line")
        
        if not text or len(text) < 3:
            continue
        
        # Try each pattern
        for pattern_idx, pattern in enumerate(REGEX_PATTERNS):
            match = re.search(pattern, text)
            if not match:
                continue
            
            value = match.group(1).strip()
            
            debug = {
                "raw_text": text,
                "extracted_value": value,
                "source": source,
                "confidence": confidence,
                "pattern_used": pattern_idx,
                "score": None,
                "rejected": None
            }
            
            # ❌ HARD REJECTS
            if re.search(DATE_RE, value):
                debug["rejected"] = "date_pattern"
                debug_rows.append(debug)
                continue
            
            if re.search(GSTIN_RE, value):
                debug["rejected"] = "gstin_pattern"
                debug_rows.append(debug)
                continue
            
            if re.fullmatch(VEHICLE_RE, value):
                debug["rejected"] = "vehicle_number"
                debug_rows.append(debug)
                continue
            
            if re.search(AMOUNT_RE, value):
                debug["rejected"] = "amount_pattern"
                debug_rows.append(debug)
                continue
            
            if not is_valid_invoice_number(value):
                debug["rejected"] = "invalid_token"
                debug_rows.append(debug)
                continue
            
            # ✅ ENHANCED SCORING
            score = 0
            
            # Base score by source
            if source == "kv":
                score += 45
            elif source == "table":
                score += 35
            else:
                score += 30
            
            # Confidence boost
            if confidence:
                score += min(confidence / 2.5, 35)
            
            # Pattern priority boost (earlier patterns are more specific)
            score += max(0, 15 - (pattern_idx * 3))
            
            # 🔑 Keyword proximity (±2 lines for better context)
            context_texts = []
            for j in range(max(0, idx - 2), min(len(textract_lines), idx + 3)):
                context_texts.append(textract_lines[j].get("text", "").lower())
            
            # Exact keyword match
            if any(k in ctx for ctx in context_texts for k in INVOICE_KEYS):
                score += 25
            # Fuzzy keyword match
            elif any(fuzzy_match_keyword(ctx, 0.75) for ctx in context_texts):
                score += 15
            
            # Position boost (invoices usually in top 30%)
            position_ratio = idx / len(textract_lines)
            if position_ratio < 0.3:
                score += 10
            
            score = round(score, 1)
            
            debug["score"] = score
            debug["rejected"] = "accepted"
            debug_rows.append(debug)
            
            candidates.append({
                "invoice_no": value,
                "score": score,
                "raw_text": text,
                "confidence": confidence
            })
    
    # ========================================================
    # 🧯 PASS 2: If no good candidates, try relaxed patterns
    # ========================================================
    
    if not candidates or max([c["score"] for c in candidates]) < 50:
        # Try to find standalone alphanumeric patterns
        for idx, item in enumerate(textract_lines):
            text = (item.get("text") or "").strip()
            
            # Skip if already processed
            if any(d.get("raw_text") == text for d in debug_rows):
                continue
            
            # Look for simple patterns like: ABC123, 123-456, etc.
            simple_pattern = r"\b([A-Z0-9]{3,}(?:[\-\/][A-Z0-9]+)*)\b"
            matches = re.findall(simple_pattern, text)
            
            for value in matches:
                if is_valid_invoice_number(value):
                    score = 40  # Lower score for fallback
                    candidates.append({
                        "invoice_no": value,
                        "score": score,
                        "raw_text": text,
                        "confidence": item.get("confidence", 0)
                    })
    
    # ========================================================
    # 🧯 FINAL DECISION LOGIC
    # ========================================================
    
    if not candidates:
        return {
            "invoice_no": None,
            "status": "EXCEPT",
            "score": 0,
            "debug": debug_rows
        }
    
    # Sort by score and pick best
    candidates.sort(key=lambda x: x["score"], reverse=True)
    best = candidates[0]
    
    # Check for duplicates with different scores
    top_candidates = [c for c in candidates if c["score"] >= best["score"] * 0.9]
    if len(top_candidates) > 1:
        # If multiple similar scores, prefer shorter invoice numbers
        best = min(top_candidates, key=lambda x: len(x["invoice_no"]))
    
    AUTO_THRESHOLD = 65
    REVIEW_THRESHOLD = 45
    
    if best["score"] >= AUTO_THRESHOLD:
        status = "AUTO"
    elif best["score"] >= REVIEW_THRESHOLD:
        status = "REVIEW"
    else:
        status = "EXCEPT"
    
    return {
        "invoice_no": best["invoice_no"],
        "status": status,
        "score": best["score"],
        "confidence": best["confidence"],
        "debug": debug_rows
    }


# ============================================================
# 🧪 TEST FUNCTION
# ============================================================

def test_extractor():
    """Test with sample data"""
    test_lines = [
        {"text": "TAX INVOICE", "confidence": 99.5, "source": "line"},
        {"text": "INVOICE No", "confidence": 99.8, "source": "line"},
        {"text": "INV-2024-001", "confidence": 98.5, "source": "line"},
        {"text": "Date: 01/01/2024", "confidence": 99.0, "source": "line"},
    ]
    
    result = extract_invoice_number(test_lines)
    print("Test Result:", result)
    return result


if __name__ == "__main__":
    test_extractor()
