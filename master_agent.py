import os
from dotenv import load_dotenv

# Load the hidden vault
load_dotenv()
import requests
import csv
import time
from datetime import datetime
import os
import json
import hmac
import hashlib
from urllib.parse import urlencode


# --- SYSTEM CONFIGURATION ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

# The Binance Testnet Keys (Simulation)
BINANCE_API_KEY =  os.getenv("BINANCE_API_KEY")
BINANCE_SECRET_KEY = os.getenv("BINANCE_SECRET_KEY")

# URLs
BINANCE_PRICE_URL = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT" # We get real live price
BINANCE_ORDER_URL = "https://testnet.binance.vision/api/v3/order" # But we send fake orders to testnet
CSV_FILENAME = "master_price_log.csv"
SLEEP_INTERVAL = 60 

# Initialize memory file if it doesn't exist
if not os.path.exists(CSV_FILENAME):
    with open(CSV_FILENAME, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Timestamp", "Symbol", "Price"])
    print(f"📁 Created new persistent memory: {CSV_FILENAME}")

print("🚀 INITIATING AUTONOMOUS EXECUTION AGENT...")

while True:
    try:
        # ---------------------------------------------------------
        # PHASE 1: DATA INGESTION
        # ---------------------------------------------------------
        print("\n📡 Fetching live market data...")
        binance_response = requests.get(BINANCE_PRICE_URL)
        binance_response.raise_for_status()
        current_price = float(binance_response.json()['price'])
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # ---------------------------------------------------------
        # PHASE 2: PERSISTENT MEMORY
        # ---------------------------------------------------------
        with open(CSV_FILENAME, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([timestamp, "BTCUSDT", current_price])
        print(f"💾 Logged: BTC at ${current_price:.2f}")

        # ---------------------------------------------------------
        # PHASE 3: CONTEXT EXTRACTION
        # ---------------------------------------------------------
        data_points = []
        with open(CSV_FILENAME, mode='r') as file:
            reader = list(csv.DictReader(file))
            last_entries = reader[-10:]
            for row in last_entries:
                data_points.append(f"Price: {row['Price']} at {row['Timestamp']}")
        
        context = "\n".join(data_points)
        prompt = f"Analyze these BTC prices and give a 2-sentence trend summary. Look for micro-trends:\n{context}"

        # ---------------------------------------------------------
        # PHASE 4: AI ORCHESTRATION (Structured Logic)
        # ---------------------------------------------------------
        if len(last_entries) >= 3:
            print("🧠 Requesting structured AI decision from Groq...")
            groq_url = "https://api.groq.com/openai/v1/chat/completions"
            system_instruction = """
            You are a quantitative trading algorithm. Analyze the micro-trend.
            You MUST output strictly in JSON format. Do not include any conversational text.
            Your JSON must contain exactly these keys:
            - 'trend': A brief 1-sentence analysis.
            - 'signal': Strictly 'BUY', 'SELL', or 'HOLD'.
            - 'confidence_score': An integer between 1 and 100.
            """
            groq_payload = {
                "model": "llama-3.1-8b-instant",
                "response_format": {"type": "json_object"},
                "messages": [
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": prompt}
                ]
            }
            groq_headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {GROQ_API_KEY}"
            }
            
            groq_response = requests.post(groq_url, headers=groq_headers, json=groq_payload)
            groq_response.raise_for_status()
            
            ai_raw_text = groq_response.json()['choices'][0]['message']['content'].strip()
            ai_decision = json.loads(ai_raw_text) 

            print(f"🤖 AI Decision: {ai_decision['signal']} (Confidence: {ai_decision['confidence_score']}%)")

            # ---------------------------------------------------------
            # PHASE 5 & 6: THE BRIDGE & THE EXECUTIONER
            # ---------------------------------------------------------
            if ai_decision['confidence_score'] > 60:
                signal = ai_decision['signal']
                print(f"📣 High confidence ({ai_decision['confidence_score']}%)! Transmitting alert...")
                
                discord_payload = {
                    "content": f"🚨 **ACTIONABLE SIGNAL: {signal}** 🚨\n*Current Price: ${current_price:,.2f}*\n*Confidence:* {ai_decision['confidence_score']}%\n\n*Analysis:* {ai_decision['trend']}"
                }
                requests.post(DISCORD_WEBHOOK_URL, json=discord_payload)
                
                if signal in ["BUY", "SELL"]:
                    print(f"⚡ SIGNING CRYPTOGRAPHIC PAYLOAD FOR {signal} ORDER...")
                    
                    order_params = {
                        "symbol": "BTCUSDT",
                        "side": signal,
                        "type": "MARKET",
                        "quantity": 0.001,
                        "timestamp": int(time.time() * 1000)
                    }
                    
                    # The HMAC-SHA256 Cryptographic Signature
                    query_string = urlencode(order_params)
                    signature = hmac.new(BINANCE_SECRET_KEY.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()
                    order_params['signature'] = signature
                    
                    headers = {"X-MBX-APIKEY": BINANCE_API_KEY}
                    
                    print(f"💸 EXECUTING LIVE {signal} ON BINANCE TESTNET...")
                    order_response = requests.post(BINANCE_ORDER_URL, headers=headers, params=order_params)
                    
                    if order_response.status_code == 200:
                        order_id = order_response.json().get('orderId')
                        print(f"✅ SUCCESS! Order Filled. ID: {order_id}")
                    else:
                        print(f"❌ EXECUTION FAILED: {order_response.text}")
            else:
                print("⚠️ Low confidence. Holding position. No actions taken.")
        else:
            print("⏳ Gathering more data points before requesting AI analysis...")

        # ---------------------------------------------------------
        # PHASE 7: THE HEARTBEAT
        # ---------------------------------------------------------
        print(f"💤 Sleeping for {SLEEP_INTERVAL} seconds...\n")
        time.sleep(SLEEP_INTERVAL)

    except Exception as e:
        print(f"⚠️ SYSTEM ERROR: {e}")
        print("🔄 Retrying in 30 seconds...")
        time.sleep(30)