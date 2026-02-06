import re

# ============================================================
# 🔒 ENHANCED AMOUNT KEYWORDS
# ============================================================

AMOUNT_KEYS = [
    # Primary keywords (highest priority)
    "grand total", "net payable", "total payable", "amount payable",
    "total amount", "invoice total", "balance due",
    
    # Secondary keywords
    "total", "amount", "net amount", "final amount",
    
    # Alternative terms
    "payable", "due", "payment", "sum total",
    
    # Multi-language support
    "कुल राशि", "total राशि"
]

# Negative keywords (amounts to avoid)
NEGATIVE_KEYS = [
    "subtotal", "sub total", "sub-total",
    "cgst", "sgst", "igst", "gst", "tax",
    "discount", "advance", "balance",
    "rate", "price", "unit price"
]

# ============================================================
# 🔒 ENHANCED CURRENCY PATTERNS
# ============================================================

# Pattern 1: With currency symbol
CURRENCY_PATTERN_1 = re.compile(
    r"(?:₹|rs\.?|inr)[\s]*([0-9]{1,3}(?:,[0-9]{2,3})*(?:\.[0-9]{2})?)",
    re.IGNORECASE
)

# Pattern 2: Without currency symbol (more permissive)
CURRENCY_PATTERN_2 = re.compile(
    r"\b([0-9]{1,3}(?:,[0-9]{2,3})*(?:\.[0-9]{2})?)\b"
)

# Pattern 3: Space-separated format (Indian style)
CURRENCY_PATTERN_3 = re.compile(
    r"\b([0-9]{1,2}(?:\s[0-9]{2})*(?:\.[0-9]{2})?)\b"
)

# ============================================================
# 💰 AMOUNT NORMALIZER
# ============================================================

def normalize_amount(val: str) -> float:
    """
    Enhanced amount normalization handling multiple formats:
    - 1,234.56
    - 1 23 45.56 (Indian format)
    - 1234.56
    """
    try:
        # Remove spaces and commas
        cleaned = val.replace(",", "").replace(" ", "")
        return round(float(cleaned), 2)
    except:
        return None

# ============================================================
# 🎯 AMOUNT VALIDATOR
# ============================================================

def is_valid_total_amount(amount: float, idx: int, total_lines: int) -> dict:
    """
    Validate if amount is likely a total amount
    Returns: dict with is_valid (bool) and reason (str)
    """
    # Too small
    if amount < 10:
        return {"is_valid": False, "reason": "too_small"}
    
    # Unreasonably large (> 10 crore)
    if amount > 100000000:
        return {"is_valid": False, "reason": "too_large"}
    
    # Suspiciously round numbers < 100 might be tax rates
    if amount < 100 and amount % 5 == 0:
        return {"is_valid": False, "reason": "likely_tax_rate"}
    
    # Position check: totals usually in bottom 50%
    position_ratio = idx / total_lines
    if position_ratio < 0.4:
        return {"is_valid": True, "reason": "position_weak"}
    
    return {"is_valid": True, "reason": "valid"}

# ============================================================
# 🔍 CONTEXT ANALYZER
# ============================================================

def analyze_context(text: str, nearby_lines: list) -> dict:
    """
    Analyze surrounding context for amount extraction
    Returns scoring adjustments
    """
    text_lower = text.lower()
    context = " ".join([line.lower() for line in nearby_lines])
    
    score_adjustments = {
        "keyword_boost": 0,
        "negative_penalty": 0,
        "position_boost": 0
    }
    
    # Check for positive keywords
    for key in AMOUNT_KEYS:
        if key in text_lower:
            if key in ["grand total", "net payable", "total payable"]:
                score_adjustments["keyword_boost"] = 30
            elif key in ["total amount", "invoice total"]:
                score_adjustments["keyword_boost"] = 25
            else:
                score_adjustments["keyword_boost"] = 15
            break
    
    # Check context (±1 line)
    for key in AMOUNT_KEYS:
        if key in context and score_adjustments["keyword_boost"] == 0:
            score_adjustments["keyword_boost"] = 10
            break
    
    # Check for negative keywords
    for neg_key in NEGATIVE_KEYS:
        if neg_key in text_lower:
            score_adjustments["negative_penalty"] = -20
            break
    
    return score_adjustments

# ============================================================
# 🧠 ENHANCED CORE EXTRACTOR
# ============================================================

def extract_total_amount(lines):
    """
    Enhanced total amount extraction with:
    - Multiple currency pattern support
    - Better context analysis
    - Improved validation
    - Multi-pass extraction
    """
    candidates = []
    debug = []
    
    total_lines = len(lines)
    
    # Pass 1: Extract with currency symbol
    for idx, item in enumerate(lines):
        text = (item.get("text") or "").strip()
        low = text.lower()
        conf = item.get("confidence", 0)
        
        if not text:
            continue
        
        # Get nearby context (±2 lines)
        nearby_lines = []
        for j in range(max(0, idx - 2), min(len(lines), idx + 3)):
            if j != idx:
                nearby_lines.append(lines[j].get("text", ""))
        
        # Analyze context
        context_analysis = analyze_context(text, nearby_lines)
        
        # Try Pattern 1 (with currency symbol)
        for m in CURRENCY_PATTERN_1.finditer(text):
            amt = normalize_amount(m.group(1))
            if not amt:
                continue
            
            validation = is_valid_total_amount(amt, idx, total_lines)
            if not validation["is_valid"]:
                debug.append({
                    "raw_text": text,
                    "extracted_amount": amt,
                    "score": 0,
                    "confidence": conf,
                    "rejected": validation["reason"]
                })
                continue
            
            # Calculate score
            score = 45  # Base score for currency symbol pattern
            
            # Confidence boost
            score += min(conf / 2, 25)
            
            # Context adjustments
            score += context_analysis["keyword_boost"]
            score += context_analysis["negative_penalty"]
            
            # Position boost (amounts in bottom 35%)
            position_ratio = idx / total_lines
            if position_ratio > 0.65:
                score += 20
            elif position_ratio > 0.5:
                score += 10
            
            # Amount size heuristic (larger amounts more likely to be totals)
            if amt > 10000:
                score += 5
            if amt > 100000:
                score += 5
            
            score = round(max(0, score), 1)
            
            candidates.append((amt, score))
            debug.append({
                "raw_text": text,
                "extracted_amount": amt,
                "score": score,
                "confidence": conf,
                "rejected": "accepted",
                "pattern": "currency_symbol"
            })
    
    # Pass 2: If no good candidates, try without currency symbol
    if not candidates or max([c[1] for c in candidates]) < 50:
        for idx, item in enumerate(lines):
            text = (item.get("text") or "").strip()
            low = text.lower()
            conf = item.get("confidence", 0)
            
            # Skip if already processed
            if any(d.get("raw_text") == text and d.get("rejected") == "accepted" for d in debug):
                continue
            
            # Only process if has amount keywords
            if not any(key in low for key in AMOUNT_KEYS):
                continue
            
            nearby_lines = []
            for j in range(max(0, idx - 2), min(len(lines), idx + 3)):
                if j != idx:
                    nearby_lines.append(lines[j].get("text", ""))
            
            context_analysis = analyze_context(text, nearby_lines)
            
            # Try Pattern 2 (without symbol)
            for m in CURRENCY_PATTERN_2.finditer(text):
                amt = normalize_amount(m.group(1))
                if not amt:
                    continue
                
                validation = is_valid_total_amount(amt, idx, total_lines)
                if not validation["is_valid"]:
                    continue
                
                # Lower base score for no-symbol pattern
                score = 35
                score += min(conf / 2, 20)
                score += context_analysis["keyword_boost"]
                score += context_analysis["negative_penalty"]
                
                position_ratio = idx / total_lines
                if position_ratio > 0.65:
                    score += 15
                
                score = round(max(0, score), 1)
                
                candidates.append((amt, score))
                debug.append({
                    "raw_text": text,
                    "extracted_amount": amt,
                    "score": score,
                    "confidence": conf,
                    "rejected": "accepted",
                    "pattern": "no_symbol"
                })
    
    # ========================================================
    # 🧯 FINAL DECISION
    # ========================================================
    
    if not candidates:
        return {
            "total_amount": None,
            "status": "EXCEPT",
            "score": 0,
            "debug": debug
        }
    
    # Sort by score
    candidates.sort(key=lambda x: x[1], reverse=True)
    best = candidates[0]
    
    # If multiple high-scoring candidates, pick largest amount
    top_candidates = [c for c in candidates if c[1] >= best[1] * 0.95]
    if len(top_candidates) > 1:
        best = max(top_candidates, key=lambda x: x[0])
    
    AUTO_THRESHOLD = 60
    REVIEW_THRESHOLD = 40
    
    if best[1] >= AUTO_THRESHOLD:
        status = "AUTO"
    elif best[1] >= REVIEW_THRESHOLD:
        status = "REVIEW"
    else:
        status = "EXCEPT"
    
    return {
        "total_amount": best[0],
        "status": status,
        "score": best[1],
        "debug": debug
    }


# ============================================================
# 🧪 TEST FUNCTION
# ============================================================

def test_extractor():
    """Test with sample data"""
    test_lines = [
        {"text": "Item 1: ₹500.00", "confidence": 99.0, "source": "line"},
        {"text": "Item 2: ₹300.00", "confidence": 99.0, "source": "line"},
        {"text": "Subtotal: ₹800.00", "confidence": 99.0, "source": "line"},
        {"text": "GST (18%): ₹144.00", "confidence": 99.0, "source": "line"},
        {"text": "Grand Total: ₹944.00", "confidence": 99.5, "source": "line"},
    ]
    
    result = extract_total_amount(test_lines)
    print("Test Result:", result)
    return result


if __name__ == "__main__":
    test_extractor()
