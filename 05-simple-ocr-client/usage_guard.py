import json
import os
from datetime import date
from config import *

def load_state():
    if not os.path.exists(STATE_FILE):
        return {
            "month": date.today().strftime("%Y-%m"),
            "monthly_spend": 0.0,
            "daily": {}
        }
    with open(STATE_FILE) as f:
        return json.load(f)

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def check_limits(pages):
    state = load_state()
    today = date.today().isoformat()
    this_month = date.today().strftime("%Y-%m")

    # reset month
    if state["month"] != this_month:
        state = {"month": this_month, "monthly_spend": 0.0, "daily": {}}

    est_cost = pages * EST_COST_PER_PAGE
    daily_spend = state["daily"].get(today, 0.0)

    if state["monthly_spend"] + est_cost > MONTHLY_USD_LIMIT:
        raise Exception("⛔ MONTHLY OCR LIMIT HIT")

    if daily_spend + est_cost > DAILY_USD_LIMIT:
        raise Exception("⛔ DAILY OCR LIMIT HIT")

    # update
    state["monthly_spend"] += est_cost
    state["daily"][today] = daily_spend + est_cost
    save_state(state)
