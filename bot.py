import os
import re
import sys
import time
import json
import random
import requests
import threading
import urllib.parse
from datetime import datetime, timedelta, timezone

# ================= কনফিগারেশন =================
BOT_TOKEN = "8864547814:AAGZY2Kc_252le4uaZhOL0AR3Ql4g3G3I7A"
BOT_USERNAME = "DRX_TM_POD_BOT" 
CHANNEL_USERNAME = "@DARK67HACK"
CHAT_ID = "@DARK67HACK"  # সিগন্যাল পাঠানোর চ্যানেল

ADMIN_ID = "8707571669"  # এডমিন আইডি

BASE_API = "https://sh-tim-faruk-vai.ai.studio/api"
LEADERBOARD_API = "https://sh-tim-faruk-vai.ai.studio/apipid.json"

DB_FILE = "users_db.json"
BD_TIMEZONE = timezone(timedelta(hours=6))

# ================= স্টিকারসমূহ =================
START_STICKER = "CAACAgUAAxkBAAICx2pgV34mvhrXYdFo074GfPCT3DxpAAIGHAACCWOZVJ54JyHk0pq6PQQ"
WIN_STICKERS = [
    "CAACAgUAAxkBAAICympgV_mYbYJ5o_ltYTUUBv7mKTr5AALSHAACQlWYVEhO4I8eBRYYPQQ",
    "CAACAgUAAxkBAAIC2GpgXkSXM2Nm8xUq97L6CewvEjVuAALUHgACWhiJVBClJA3AM_g7PQQ"
]
LOSS_STICKER = "CAACAgUAAxkBAAICzGpgWC6gUjMbKd5TvjfoCeqHPrrtAAJOGQACxAuZVNxk4HDx8tskPQQ"
MORNING_STICKER = "CAACAgUAAxkBAAIC0GpgWErTJk46Z_CfSizMZsi2vIU0AAKaFwACE0qZVBcum6ql5maTPQQ"

# ================= ট্রেডার তালিকা =================
ALL_TRADERS = [
    {"name": "Dark Horse", "slug": "dark-horse"},
    {"name": "Shark Tank", "slug": "shark-tank"},
    {"name": "Subs Pro VIP", "slug": "subs"},
    {"name": "Dragon Pro VIP", "slug": "dragon-pro"},
    {"name": "Tiger Pro VIP", "slug": "tiger-pro"},
    {"name": "Dragon King", "slug": "dragon-king"},
    {"name": "Phoenix VIP", "slug": "phoenix-vip"},
    {"name": "Eagle Eye", "slug": "eagle-eye"},
    {"name": "Lion Heart", "slug": "lion-heart"},
    {"name": "Thunder Bolt", "slug": "thunder-bolt"},
    {"name": "Shadow X", "slug": "shadow-x"},
    {"name": "Cobra Strike", "slug": "cobra-strike"},
    {"name": "Wolf Pack", "slug": "wolf-pack"},
    {"name": "Blaze Pro", "slug": "blaze-pro"},
    {"name": "Viper Gold", "slug": "viper-gold"},
    {"name": "Rocket Star", "slug": "rocket-star"},
    {"name": "Storm Chaser", "slug": "storm-chaser"},
    {"name": "Ninja Master", "slug": "ninja-master"},
    {"name": "Falcon Rush", "slug": "falcon-rush"},
    {"name": "Panther VIP", "slug": "panther-vip"},
    {"name": "Ghost Rider", "slug": "ghost-rider"},
    {"name": "Bullet Pro", "slug": "bullet-pro"},
    {"name": "Quantum X", "slug": "quantum-x"},
    {"name": "Apex Titan", "slug": "apex-titan"},
    {"name": "Nova Prime", "slug": "nova-prime"},
    {"name": "Stealth Hawk", "slug": "stealth-hawk"},
    {"name": "Omega Force", "slug": "omega-force"},
    {"name": "Zenith Pro", "slug": "zenith-pro"},
    {"name": "Crypto Wolf", "slug": "crypto-wolf"},
    {"name": "Rapid Fire", "slug": "rapid-fire"},
    {"name": "Iron Pulse", "slug": "iron-pulse"},
    {"name": "Shadow Blade", "slug": "shadow-blade"}
]

USER_SESSIONS = {}
LAST_UPDATE_ID = 0

# সিগন্যাল কন্ট্রোল স্টেট
IS_ACTIVE = False
STOP_PENDING = False
LAST_WAS_WIN = True
LAST_MORNING_STICKER_DATE = None
SCHEDULES = [(14, 0, 15, 0), (17, 0, 18, 0)]
CURRENT_TRADER_INDEX = 0  # ০ = টপ ১ নম্বর ট্রেডার, লস হলে বাড়বে

# ================= ফন্ট ও কালার হেল্পার =================
def to_premium(text):
    mapping = str.maketrans(
        "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789",
        "𝐀𝐁𝐂𝐃𝐄𝐅𝐆𝐇𝐈𝐉𝐊𝐋𝐌𝐍𝐎𝐏𝐐𝐑𝐒𝐓𝐔𝐕𝐖𝐗𝐘𝐙𝐚𝐛𝐜𝐝𝐞𝐟𝐠𝐡𝐢𝐣𝐤𝐥𝐦𝐧𝐨𝐩𝐪𝐫𝐬𝐭𝐮𝐯𝐰𝐱𝐲𝐳𝟎𝟏𝟐𝟑𝟒𝟓𝟔𝟕𝟖𝟗"
    )
    return str(text).translate(mapping)

def format_12hr(hour, minute):
    ampm = "AM" if hour < 12 else "PM"
    h12 = hour % 12
    if h12 == 0: h12 = 12
    return f"{h12:02d}:{minute:02d} {ampm}"

def get_number_color(num):
    try:
        n = int(num)
        if n in [1, 3, 7, 9]:
            return "GREEN 🟢"
        elif n in [2, 4, 6, 8]:
            return "RED 🔴"
        elif n == 0:
            return "RED+VIOLET 🔴🟣"
        elif n == 5:
            return "GREEN+VIOLET 🟢🟣"
    except:
        pass
    return ""

def parse_time_command(text):
    match = re.search(r'/TM\s+(\d{1,2}):(\d{2})\s*(AM|PM)?\s*-\s*(\d{1,2}):(\d{2})\s*(AM|PM)?', text, re.IGNORECASE)
    if match:
        sh, sm, sampm, eh, em, eampm = match.groups()
        sh, sm, eh, em = int(sh), int(sm), int(eh), int(em)
        if sampm:
            sampm = sampm.upper()
            if sampm == 'PM' and sh != 12: sh += 12
            if sampm == 'AM' and sh == 12: sh = 0
        else:
            if sh < 12 and sh != 0: sh += 12

        if eampm:
            eampm = eampm.upper()
            if eampm == 'PM' and eh != 12: eh += 12
            if eampm == 'AM' and eh == 12: eh = 0
        else:
            if eh < 12 and eh != 0: eh += 12
        return (sh, sm, eh, em)
    return None

# ================= ডাটাবেস হ্যান্ডলার =================
def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                db = json.load(f)
                if "__config__" not in db:
                    db["__config__"] = {"bypass_password": None}
                return db
        except Exception:
            pass
    return {"__config__": {"bypass_password": None}}

def save_db(db):
    try:
        with open(DB_FILE, "w") as f:
            json.dump(db, f)
    except Exception as e:
        print(f"[-] DB Error: {e}")

USERS_DB = load_db()

# ================= টেলিগ্রাম সেন্ডার =================
def send_telegram_msg(chat_id, text, parse_mode="HTML"):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        res = requests.post(url, json={"chat_id": chat_id, "text": text, "parse_mode": parse_mode}, timeout=5).json()
        return res
    except Exception as e:
        print(f"[-] SendMsg Error: {e}")
        return {}

def send_telegram_sticker(chat_id, sticker_id):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendSticker"
    try:
        return requests.post(url, json={"chat_id": chat_id, "sticker": sticker_id}, timeout=5).json()
    except:
        return {}

def answer_callback(cb_id, text="", show_alert=False):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/answerCallbackQuery"
    try:
        requests.post(url, json={"callback_query_id": cb_id, "text": text, "show_alert": show_alert}, timeout=2)
    except:
        pass

def check_channel_member(user_id):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getChatMember"
    params = {"chat_id": CHANNEL_USERNAME, "user_id": user_id}
    try:
        res = requests.get(url, params=params, timeout=3).json()
        if res.get("ok"):
            status = res["result"]["status"]
            return status in ["member", "administrator", "creator"]
    except:
        pass
    return False

def get_user_task_info(user_id):
    user_id = str(user_id)
    current_day = int(time.time() + 21600) // 86400
    if user_id not in USERS_DB:
        USERS_DB[user_id] = {"joined_day": current_day, "referrals": [], "unlocked_days": []}
        save_db(USERS_DB)
    user_data = USERS_DB[user_id]
    days_active = current_day - user_data.get("joined_day", current_day)
    target_shares = 2 + days_active
    current_referrals = len(user_data.get("referrals", []))
    is_unlocked_today = str(current_day) in user_data.get("unlocked_days", [])
    return target_shares, current_referrals, is_unlocked_today, current_day

# ================= ট্রেডার API ডেটা =================
def fetch_leaderboard():
    try:
        res = requests.get(LEADERBOARD_API, timeout=3)
        if res.status_code == 200:
            return res.json()
    except:
        pass
    return {}

def fetch_trader_data(slug):
    url = f"{BASE_API}/apipid-{slug}.json"
    try:
        res = requests.get(url, timeout=3)
        if res.status_code == 200:
            return res.json()
    except:
        pass
    return {}

def get_countdown():
    return 30 - (int(time.time()) % 30)

def get_timer_display():
    sec = get_countdown()
    blocks = int((sec / 30.0) * 15)
    bar = "▓" * blocks + "░" * (15 - blocks)
    return f"⏳ {sec:02d}S [{bar}]"

# ================= 🧠 হিউম্যান ব্রেন লাইভ সিলেকশন =================
def get_current_active_trader_data(rank_offset=0):
    lb = fetch_leaderboard()
    top_traders = lb.get("top_3_traders", [])
    
    ordered_slugs = []
    if top_traders and isinstance(top_traders, list):
        for candidate in top_traders:
            c_name = candidate.get("name", "").strip().lower()
            for t in ALL_TRADERS:
                if t["name"].strip().lower() == c_name:
                    if t["slug"] not in ordered_slugs:
                        ordered_slugs.append(t["slug"])
                    break

    for fallback in ["dark-horse", "shark-tank", "subs", "dragon-pro", "tiger-pro"]:
        if fallback not in ordered_slugs:
            ordered_slugs.append(fallback)

    target_slug = ordered_slugs[rank_offset % len(ordered_slugs)]
    t_data = fetch_trader_data(target_slug)

    if not t_data or not t_data.get("period"):
        for alt in ordered_slugs:
            t_data = fetch_trader_data(alt)
            if t_data and t_data.get("period"):
                break

    return t_data

def send_prediction_signal(period, prediction, pred_num):
    short_period = str(period)[-6:]
    
    if prediction == "BIG":
        digits_pool = ['5', '6', '7', '8', '9']
    else:
        digits_pool = ['0', '1', '2', '3', '4']
        
    color_info = get_number_color(pred_num) if pred_num is not None else ""
    if color_info:
        num_line = f"⚡ Number   ➤  {pred_num} ({color_info})"
    elif pred_num is not None:
        num_line = f"⚡ Number   ➤  {pred_num}"
    else:
        num_line = ""

    if pred_num is not None and str(pred_num) in digits_pool:
        other_digit = random.choice([d for d in digits_pool if d != str(pred_num)])
        digits = f"{pred_num}/{other_digit}"
    else:
        digits = "/".join(random.sample(digits_pool, 2))

    text = f"""🌿🍁🌿 {prediction} SIGNAL 🌿🍁🌿
▱▱▱▱▱▱▱▱▱▱▱▱▱▱
💎 Period   ➤  {short_period}
🎯 Action   ➤  BET {prediction} 🌹
{num_line}
⚡ Digits   ➤  {digits}
▱▱▱▱▱▱▱▱▱▱▱▱▱▱"""
    send_telegram_msg(CHAT_ID, text)
    print(f"[+] [SIGNAL SENT] Period: {short_period} | Action: {prediction} | Num: {pred_num}")

# ================= সেশন কন্ট্রোল লজিক =================
def start_signal_session(manual=False):
    global IS_ACTIVE, STOP_PENDING, CURRENT_TRADER_INDEX
    if not IS_ACTIVE:
        IS_ACTIVE = True
        STOP_PENDING = False
        CURRENT_TRADER_INDEX = 0
        send_telegram_sticker(CHAT_ID, START_STICKER)
        trigger = "Manual (/TA)" if manual else "Schedule"
        send_telegram_msg(
            CHAT_ID, 
            f"🚀 <b>VIP SIGNAL SESSION STARTED!</b>\n\n"
            f"🧠 <i>AI Top-Trader Brain Activated.</i>\n"
            f"⏰ <b>Trigger:</b> {trigger}\n"
            f"🎯 <i>Live predictions broadcasting!</i>"
        )
        print(f"[+] Signal Session Started via {trigger}")

def trigger_stop_signal_session():
    global STOP_PENDING
    STOP_PENDING = True
    print("[*] Stop requested. Waiting for WIN before closing session...")

def execute_session_close():
    global IS_ACTIVE, STOP_PENDING, CURRENT_TRADER_INDEX
    IS_ACTIVE = False
    STOP_PENDING = False
    CURRENT_TRADER_INDEX = 0
    send_telegram_sticker(CHAT_ID, START_STICKER)
    send_telegram_msg(
        CHAT_ID,
        "🛑 <b>SESSION CLOSED SAFELY!</b>\n\n"
        "✅ <i>Successfully completed with a WIN.</i>\n"
        "ধন্যবাদ সবাইকে। পরবর্তী সেশনে আবার দেখা হবে! 🌹"
    )
    print("[-] Session Closed Safely on WIN.")

def is_in_schedule(now):
    c24 = now.hour * 60 + now.minute
    c12 = (now.hour % 12) * 60 + now.minute

    for (sh, sm, eh, em) in SCHEDULES:
        s24 = sh * 60 + sm
        e24 = eh * 60 + em
        if s24 <= e24:
            if s24 <= c24 < e24: return True
        else:
            if c24 >= s24 or c24 < e24: return True

        s12 = (sh % 12) * 60 + sm
        e12 = (eh % 12) * 60 + em
        if s12 <= e12:
            if s12 <= c12 < e12: return True
        else:
            if c12 >= s12 or c12 < e12: return True

    return False

# ================= ⚡ চ্যানেলের অটো সিগন্যাল ও রিয়েল উইন/লস ডিটেকশন =================
def channel_signal_engine():
    global IS_ACTIVE, STOP_PENDING, LAST_WAS_WIN, LAST_MORNING_STICKER_DATE, CURRENT_TRADER_INDEX
    
    last_processed_period = None
    target_prediction_info = None

    print("[*] Channel Signal Engine Active & Monitoring Top Traders...")

    while True:
        try:
            now = datetime.now(BD_TIMEZONE)

            if now.hour == 5 and now.minute == 0:
                if LAST_MORNING_STICKER_DATE != now.date():
                    send_telegram_sticker(CHAT_ID, MORNING_STICKER)
                    LAST_MORNING_STICKER_DATE = now.date()

            if is_in_schedule(now):
                if not IS_ACTIVE and not STOP_PENDING:
                    start_signal_session(manual=False)
            else:
                if IS_ACTIVE and not STOP_PENDING:
                    trigger_stop_signal_session()

            # অ্যাক্টিভ ট্রেডারের ডেটা সংগ্রহ
            t_data = get_current_active_trader_data(CURRENT_TRADER_INDEX)
            if t_data:
                curr_period = str(t_data.get("period", "")).strip()
                main_pred = t_data.get("main_prediction", {})
                pred_action = str(main_pred.get("prediction", "")).strip().upper()
                pred_num = main_pred.get("predicted_number", None)
                history = t_data.get("history", [])

                # ১. রিয়েল-টাইম উইন/লস স্বাধীন ভেরিফিকেশন (Mathematical Calculation)
                if target_prediction_info and history:
                    target_p = str(target_prediction_info["period"]).strip()
                    
                    # হিস্ট্রি থেকে ঠিক আমাদের প্রেডিক্ট করা পিরিয়ডটি খুঁজে বের করা
                    matched_item = None
                    for item in history:
                        h_p = str(item.get("period", "")).strip()
                        # শেষ ৫ ডিজিট বা সম্পূর্ণ পিরিয়ড দিয়ে হুবহু মিল খোঁজা
                        if h_p == target_p or (len(target_p) >= 5 and h_p.endswith(target_p[-5:])) or (len(h_p) >= 5 and target_p.endswith(h_p[-5:])):
                            matched_item = item
                            break
                    
                    # যদি নির্দিষ্ট পিরিয়ডটি হিস্ট্রিতে এসে থাকে এবং ড্র নম্বর পাওয়া যায়
                    if matched_item:
                        actual_num_raw = matched_item.get("actual_number")
                        if actual_num_raw is not None and str(actual_num_raw).strip() not in ["", "-", "None"]:
                            try:
                                actual_num = int(actual_num_raw)
                                # ০-৪ হলে SMALL, ৫-৯ হলে BIG (স্বাধীন গাণিতিক সত্য)
                                actual_outcome = "BIG" if actual_num >= 5 else "SMALL"
                                
                                predicted_action = target_prediction_info["action"]
                                
                                # প্রেডিকশন এবং ড্র হওয়া ফলাফল মিলিয়ে দেখা
                                if predicted_action == actual_outcome:
                                    # ✅ প্রকৃত উইন
                                    send_telegram_sticker(CHAT_ID, random.choice(WIN_STICKERS))
                                    LAST_WAS_WIN = True
                                    CURRENT_TRADER_INDEX = 0  # উইন হলে পুনরায় শীর্ষ ১ নম্বরে রিসেট
                                    print(f"[+] [REAL WIN] Period: {target_p} | Pred: {predicted_action} | Actual: {actual_num} ({actual_outcome})")
                                    if STOP_PENDING:
                                        execute_session_close()
                                else:
                                    # ❌ প্রকৃত লস
                                    send_telegram_sticker(CHAT_ID, LOSS_STICKER)
                                    LAST_WAS_WIN = False
                                    CURRENT_TRADER_INDEX += 1  # লস হলে পেছনের ২য় সেরা ট্রেডারে সুইচ
                                    print(f"[-] [REAL LOSS] Period: {target_p} | Pred: {predicted_action} | Actual: {actual_num} ({actual_outcome}) -> Next Trader Rank #{CURRENT_TRADER_INDEX}")

                                target_prediction_info = None  # এই রাউন্ডের রেজাল্ট কমপ্লিট
                            except ValueError:
                                pass

                # ২. নতুন সিগন্যাল চ্যানেলে পাঠানো (রেজাল্ট শেষ হলে বা নতুন রাউন্ড শুরু হলে)
                if IS_ACTIVE and curr_period and curr_period != last_processed_period and target_prediction_info is None:
                    if pred_action in ["BIG", "SMALL"]:
                        send_prediction_signal(curr_period, pred_action, pred_num)
                        target_prediction_info = {
                            "period": curr_period,
                            "action": pred_action,
                            "num": pred_num
                        }
                        last_processed_period = curr_period

        except Exception as e:
            print(f"[-] Signal Engine Error: {e}")

        time.sleep(1)

# ================= টার্মিনাল মেনু ও কীবোর্ড ভিউ =================
def send_welcome_task_menu(chat_id, msg_id=None):
    target, current, _, _ = get_user_task_info(chat_id)
    text = (
        f"<b>{to_premium('WELCOME TO WINGO PREMIUM BOT')}</b>\n\n"
        "আসসালামু আলাইকুম। আশা করি সকলে ভালো আছেন।\n\n"
        "এই 𝐏𝐑𝐄𝐌𝐈𝐔𝐌 𝐓𝐑𝐀𝐃𝐈𝐍𝐆 𝐁𝐎𝐓 ব্যবহার করার জন্য নিচের শর্ত পূরণ করুন <b>অথবা</b> এডমিনের পাসওয়ার্ড দিন:\n\n"
        f"১. অফিশিয়াল চ্যানেলে জয়েন থাকতে হবে।\n"
        f"২. প্রথমে <b>২ জন</b> রিয়েল রেফার করতে হবে। এরপর প্রতিদিন <b>১ জন</b> করে।\n\n"
        f"🎯 আপনার টার্গেট: <b>{to_premium(str(target))}</b> জন।\n"
        f"👥 রেজিষ্টার করেছে: <b>{to_premium(str(current))}</b> জন।\n\n"
        "🔑 <i>পাসওয়ার্ড থাকলে সরাসরি লিখে সেন্ড করুন।</i>"
    )
    channel_link = f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}"
    personal_ref_link = f"https://t.me/{BOT_USERNAME}?start={chat_id}"
    
    encoded_ref = urllib.parse.quote(personal_ref_link)
    encoded_txt = urllib.parse.quote("Join Premium WinGo Prediction Terminal")
    share_url = f"https://t.me/share/url?url={encoded_ref}&text={encoded_txt}"

    keyboard = [
        [{"text": to_premium("JOIN CHANNEL"), "url": channel_link}],
        [{"text": to_premium("SHARE LINK"), "url": share_url}],
        [{"text": to_premium("VERIFY REFERRALS"), "callback_data": "verify_task"}]
    ]
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML", "reply_markup": {"inline_keyboard": keyboard}}

    if msg_id:
        payload["message_id"] = msg_id
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText"
    else:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    try:
        res = requests.post(url, json=payload, timeout=5).json()
        if res.get("ok"):
            save_msg_id = msg_id if msg_id else res["result"]["message_id"]
            USER_SESSIONS[str(chat_id)] = {"msg_id": save_msg_id, "view": "task", "slug": None}
    except Exception as e:
        print(f"[-] Task Menu Error: {e}")

def build_menu_markup():
    leaderboard = fetch_leaderboard()
    keyboard = [[{"text": get_timer_display(), "callback_data": "noop"}]]

    top_traders = leaderboard.get("top_3_traders", [])
    top_names_api = [t.get("name", "").strip().lower() for t in top_traders if t.get("name")]

    ordered_traders = []
    seen_slugs = set()

    for t_name in top_names_api:
        for t in ALL_TRADERS:
            if t["name"].strip().lower() == t_name and t["slug"] not in seen_slugs:
                ordered_traders.append(t)
                seen_slugs.add(t["slug"])
                break

    for t in ALL_TRADERS:
        if t["slug"] not in seen_slugs:
            ordered_traders.append(t)
            seen_slugs.add(t["slug"])

    row = []
    for t in ordered_traders:
        row.append({"text": to_premium(t["name"].upper()), "callback_data": f"open_{t['slug']}"})
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row: keyboard.append(row)
    return to_premium("WINGO 30SEC PREDICTION TERMINAL"), keyboard

def build_market_markup(slug):
    data = fetch_trader_data(slug)
    keyboard = []
    full_target_period = str(data.get("period", "--------"))
    period_8 = full_target_period[-8:] if len(full_target_period) >= 8 else full_target_period

    main_pred = data.get("main_prediction", {})
    action = str(main_pred.get("prediction", "-")).upper()
    pred_num = str(main_pred.get("predicted_number", "-"))

    keyboard.append([{"text": to_premium(f"PERIOD: {period_8}"), "callback_data": "noop"}])
    keyboard.append([{"text": get_timer_display(), "callback_data": "noop"}])
    keyboard.append([
        {"text": to_premium(action), "callback_data": "noop"},
        {"text": to_premium(f"NUM: {pred_num}"), "callback_data": "noop"},
        {"text": to_premium("🔙 BACK"), "callback_data": "back_to_menu"}
    ])

    history = data.get("history", [])[:10]
    for item in history:
        period_4 = str(item.get("period", ""))[-4:]
        actual_num = str(item.get("actual_number", "-"))
        pred = str(item.get("prediction", "-")).upper()
        res = str(item.get("result", "-")).upper()
        keyboard.append([
            {"text": to_premium(period_4 if period_4 else "----"), "callback_data": "noop"},
            {"text": to_premium(actual_num), "callback_data": "noop"},
            {"text": to_premium(pred), "callback_data": "noop"},
            {"text": to_premium(res), "callback_data": "noop"}
        ])

    trader_name = data.get("trader_name", slug.upper()).upper()
    text_title = f"<b>{to_premium('WINGO 30S LIVE:')}</b>\n{to_premium(trader_name)}"
    return text_title, keyboard

def send_main_menu(chat_id, msg_id=None):
    text, markup = build_menu_markup()
    payload = {"chat_id": chat_id, "text": f"<b>{text}</b>", "parse_mode": "HTML", "reply_markup": {"inline_keyboard": markup}}
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText" if msg_id else f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    if msg_id: payload["message_id"] = msg_id
    try:
        res = requests.post(url, json=payload, timeout=5).json()
        if res.get("ok"):
            save_msg_id = msg_id if msg_id else res["result"]["message_id"]
            USER_SESSIONS[str(chat_id)] = {"msg_id": save_msg_id, "view": "menu", "slug": None}
    except Exception as e:
        print(f"[-] send_main_menu Error: {e}")

def switch_view(chat_id, msg_id, view, slug=None):
    if view == "menu":
        text, markup = build_menu_markup()
        text = f"<b>{text}</b>"
    else:
        text, markup = build_market_markup(slug)

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText"
    payload = {"chat_id": chat_id, "message_id": msg_id, "text": text, "parse_mode": "HTML", "reply_markup": {"inline_keyboard": markup}}
    try:
        requests.post(url, json=payload, timeout=4)
        USER_SESSIONS[str(chat_id)] = {"msg_id": msg_id, "view": view, "slug": slug}
    except:
        pass

def live_update_keyboard(chat_id, msg_id, view, slug):
    if view == "menu":
        _, markup = build_menu_markup()
    else:
        _, markup = build_market_markup(slug)

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageReplyMarkup"
    payload = {"chat_id": chat_id, "message_id": msg_id, "reply_markup": {"inline_keyboard": markup}}
    try:
        requests.post(url, json=payload, timeout=3)
    except:
        pass

def realtime_sync_engine():
    while True:
        try:
            for chat_id, session in list(USER_SESSIONS.items()):
                if session.get("view") in ["menu", "market"]:
                    live_update_keyboard(chat_id, session["msg_id"], session["view"], session.get("slug"))
        except:
            pass
        time.sleep(2)

# ================= সেন্ট্রাল মেসেজ লিসেনার =================
def process_single_update(item):
    global SCHEDULES
    
    msg = item.get("message") or item.get("channel_post")
    if msg and "text" in msg:
        sender_id = str(msg.get("from", {}).get("id", ""))
        chat_id = str(msg["chat"]["id"])
        msg_text = msg["text"].strip()
        cmd_upper = msg_text.upper()

        is_admin_user = (sender_id == ADMIN_ID or chat_id == ADMIN_ID)
        is_channel_action = (chat_id == CHAT_ID or CHANNEL_USERNAME.replace("@", "") in chat_id)

        # এডমিন কমান্ড
        if is_admin_user or is_channel_action:
            if cmd_upper == "/TA":
                start_signal_session(manual=True)
                send_telegram_msg(chat_id, "✅ লাইভ সিগন্যাল সেশন সাথে সাথে শুরু করা হয়েছে!")
                return
            elif cmd_upper == "/TOFF":
                trigger_stop_signal_session()
                send_telegram_msg(chat_id, "⏳ সেশন স্টপ মোডে গেছে। পরবর্তী WIN হওয়ার পর নিরাপদভাবে অফ হবে।")
                return
            elif cmd_upper.startswith("/TM"):
                new_sched = parse_time_command(msg_text)
                if new_sched:
                    SCHEDULES = [new_sched]
                    sh, sm, eh, em = new_sched
                    txt = f"✅ নতুন সিগন্যাল টাইম সেট করা হয়েছে:\n🕒 {format_12hr(sh, sm)} থেকে {format_12hr(eh, em)} (BD Time)"
                    send_telegram_msg(CHAT_ID, txt)
                    send_telegram_msg(chat_id, "✅ শিডিউল আপডেট সফল হয়েছে।")
                    
                    now = datetime.now(BD_TIMEZONE)
                    if is_in_schedule(now):
                        start_signal_session(manual=True)
                return
            elif msg_text.startswith("/admin "):
                new_pass = msg_text.split(" ", 1)[1].strip()
                USERS_DB["__config__"]["bypass_password"] = new_pass
                save_db(USERS_DB)
                send_telegram_msg(chat_id, f"✅ <b>Bypass password set to:</b> {new_pass}")
                return

        # পাসওয়ার্ড বাইপাস
        global_pass = USERS_DB.get("__config__", {}).get("bypass_password")
        if global_pass and msg_text == global_pass:
            _, _, _, current_day = get_user_task_info(chat_id)
            if "unlocked_days" not in USERS_DB[chat_id]:
                USERS_DB[chat_id]["unlocked_days"] = []
            if str(current_day) not in USERS_DB[chat_id]["unlocked_days"]:
                USERS_DB[chat_id]["unlocked_days"].append(str(current_day))
                save_db(USERS_DB)
            send_telegram_msg(chat_id, "✅ <b>𝐏𝐀𝐒𝐒𝐖𝐎𝐑𝐃 𝐀𝐂𝐂𝐄𝐏𝐓𝐄𝐃!</b>\nআপনি আজকের জন্য রেফারাল ছাড়াই ভিআইপি বট আনলক করেছেন।")
            send_main_menu(chat_id)
            return

        # রেফারাল ট্র্যাকিং
        if msg_text.startswith("/start ") and len(msg_text.split()) > 1:
            referrer_id = msg_text.split()[1].strip()
            if chat_id not in USERS_DB:
                get_user_task_info(chat_id)
                if referrer_id in USERS_DB and referrer_id != chat_id:
                    if "referrals" not in USERS_DB[referrer_id]:
                        USERS_DB[referrer_id]["referrals"] = []
                    if chat_id not in USERS_DB[referrer_id]["referrals"]:
                        USERS_DB[referrer_id]["referrals"].append(chat_id)
                        save_db(USERS_DB)

        # সাধারণ ইউজার টাস্ক মেনু
        is_member = check_channel_member(chat_id)
        target, current_refs, is_unlocked, _ = get_user_task_info(chat_id)
        if is_unlocked and is_member:
            send_main_menu(chat_id)
        else:
            send_welcome_task_menu(chat_id)

    # বাটন কলব্যাক হ্যান্ডলার
    elif "callback_query" in item:
        cb = item["callback_query"]
        cb_id = cb["id"]
        data = cb.get("data", "")
        chat_id = str(cb["message"]["chat"]["id"])
        msg_id = cb["message"]["message_id"]

        if data == "verify_task":
            is_member = check_channel_member(chat_id)
            target, _, is_unlocked, current_day = get_user_task_info(chat_id)
            if not is_member:
                answer_callback(cb_id, "Access Denied: You must join the channel first.", show_alert=True)
            else:
                raw_referrals = USERS_DB[chat_id].get("referrals", [])
                valid_referrals = 0
                fake_referrals = 0
                for ref_id in raw_referrals:
                    if check_channel_member(ref_id):
                        valid_referrals += 1
                    else:
                        fake_referrals += 1

                if valid_referrals < target:
                    rem = target - valid_referrals
                    alert_text = f"Access Denied: {rem} more REAL users must JOIN the channel."
                    if fake_referrals > 0:
                        alert_text += f"\n\n⚠️ Detected {fake_referrals} fake referrals!"
                    answer_callback(cb_id, alert_text, show_alert=True)
                    send_welcome_task_menu(chat_id, msg_id)
                else:
                    if not is_unlocked:
                        if "unlocked_days" not in USERS_DB[chat_id]:
                            USERS_DB[chat_id]["unlocked_days"] = []
                        USERS_DB[chat_id]["unlocked_days"].append(str(current_day))
                        save_db(USERS_DB)
                    answer_callback(cb_id, "Access Granted. Real Referrals Verified! ✅", show_alert=False)
                    send_main_menu(chat_id, msg_id)

        elif data.startswith("open_"):
            selected_slug = data.replace("open_", "")
            switch_view(chat_id, msg_id, "market", selected_slug)
            answer_callback(cb_id)

        elif data == "back_to_menu":
            switch_view(chat_id, msg_id, "menu", None)
            answer_callback(cb_id)

        else:
            answer_callback(cb_id)

# ================= সেন্ট্রাল টেলিগ্রাম লিসেনার =================
def telegram_listener():
    global LAST_UPDATE_ID, BOT_USERNAME
    
    try:
        me = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getMe", timeout=5).json()
        if not me.get("ok"):
            print("❌ [ERROR] Bot Token Invalid!")
            return
        BOT_USERNAME = me["result"]["username"]
        print(f"✅ Bot Connected: @{BOT_USERNAME}")
    except Exception as e:
        print(f"[-] Connection Error: {e}")

    try:
        requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook?drop_pending_updates=true", timeout=4)
    except:
        pass

    print("[*] Listener Active & Ready for Commands.")

    while True:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
        params = {"offset": LAST_UPDATE_ID + 1, "timeout": 2}
        try:
            res = requests.get(url, params=params, timeout=5).json()
            if res.get("ok"):
                for item in res["result"]:
                    LAST_UPDATE_ID = item["update_id"]
                    threading.Thread(target=process_single_update, args=(item,), daemon=True).start()
        except:
            pass

        time.sleep(0.2)

# ================= এন্ট্রি পয়েন্ট =================
if __name__ == "__main__":
    t_sync = threading.Thread(target=realtime_sync_engine, daemon=True)
    t_sync.start()

    t_signal = threading.Thread(target=channel_signal_engine, daemon=True)
    t_signal.start()

    telegram_listener()
