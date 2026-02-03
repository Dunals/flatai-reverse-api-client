import requests
import re
import random
import string
import time
import os

# --- CONFIGURATION ---
HOME_URL = "https://flatai.org/"
API_URL = "https://flatai.org/wp-admin/admin-ajax.php"
OUTPUT_FOLDER = "flatai_images"

# --- LIGHTNING PROXIES ---
LP_HOST = ""
LP_PORT = ""
LP_USER_BASE = ""
LP_PASS = ""

# --- SETTINGS ---
CURRENT_MODEL = "flataipro"
MAX_RETRIES = 3 

def get_sticky_proxy():
    """Generates a NEW session ID/IP every time"""
    session_id = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    final_username = f"{LP_USER_BASE}-session-{session_id}-sessTime-5" 
    proxy_url = f"http://{final_username}:{LP_PASS}@{LP_HOST}:{LP_PORT}"
    
    print(f"   ♻️  New Proxy Session: ...{session_id}")
    return {"http": proxy_url, "https": proxy_url}

def get_nonce(session):
    """Fetches the homepage to extract the security nonce"""
    print("   🕵️  Handshaking (Finding Keys)...")
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Upgrade-Insecure-Requests": "1"
        }
        
        response = session.get(f"{HOME_URL}?t={int(time.time())}", headers=headers, timeout=30)
        html = response.text
        
        match = re.search(r'["\']ai_generate_image_nonce["\']\s*:\s*["\']([a-zA-Z0-9]+)["\']', html)
        
        if match: 
            nonce = match.group(1)
            # print(f"   🔑 Found Nonce: {nonce}") 
            return nonce

        print("   ❌ Key not found on homepage.")
        return None

    except Exception as e:
        print(f"   💥 Handshake Failed: {e}")
        return None

def generate_image(prompt, session, nonce):
    print(f"   🚀 Generating: '{prompt}'")
    
    payload = {
        "action": "ai_generate_image",
        "nonce": nonce,
        "prompt": prompt,
        "aspect_ratio": "1:1",
        "seed": random.randint(100000000, 999999999),
        "style_model": CURRENT_MODEL
    }
    
    # --- CRITICAL HEADERS ---
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Origin": "https://flatai.org",
        "Referer": "https://flatai.org/",
        "X-Requested-With": "XMLHttpRequest", 
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Sec-Ch-Ua": '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin"
    }

    try:
        response = session.post(API_URL, data=payload, headers=headers, timeout=60)
        
        if response.status_code == 200:
            # Check if it's a valid JSON response
            try:
                data = response.json()
            except:
                print(f"   ⚠️ Response is not JSON: {response.text[:50]}...")
                return None

            if data.get("success") == True:
                images = data["data"].get("images", [])
                if images:
                    return images[0]
            else:
                print(f"   ⚠️ API Refused (Logic): {data}")
                
        else:
            print(f"   ❌ HTTP Error {response.status_code}")

    except Exception as e:
        print(f"   💥 Connection Error: {e}")
    
    return None

def download_image(url):
    if not url: return
    try:
        print("   ⬇️  Downloading Image...")
        r = requests.get(url, timeout=30)
        if r.status_code == 200:
            filename = f"{OUTPUT_FOLDER}/flat_{CURRENT_MODEL}_{int(time.time())}.jpg"
            with open(filename, "wb") as f:
                f.write(r.content)
            print(f"   🎉 Saved: {filename}")
            return True
    except Exception as e:
        print(f"   💥 Download failed: {e}")
    return False

# --- MAIN LOOP ---
if __name__ == "__main__":
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)

    print(f"--- FlatAI Auto-Retry System ({CURRENT_MODEL}) ---")
    
    while True:
        prompt = input("\nEnter Prompt (or 'exit'): ")
        if prompt.lower() == "exit": break
        
        success = False
        
        # RETRY LOOP
        for attempt in range(1, MAX_RETRIES + 1):
            print(f"\n⚡ Attempt {attempt}/{MAX_RETRIES}...")
            
            # 1. Start Fresh Session & IP
            s = requests.Session()
            try:
                # Set Proxy
                proxies = get_sticky_proxy()
                s.proxies.update(proxies)
                
                # 2. Get Nonce
                nonce = get_nonce(s)
                
                if nonce:
                    # 3. Generate
                    img_link = generate_image(prompt, s, nonce)
                    
                    if img_link:
                        # 4. Download
                        if download_image(img_link):
                            success = True
                            break # Break the Retry Loop
            except Exception as e:
                print(f"   ⚠️ Critical Error in loop: {e}")
            
            if not success:
                print("   ⚠️ Failed. Switching IP and Retrying...")
                time.sleep(2) # Give a small breather
        
        if not success:
            print("\n❌ All retries failed for this prompt. Try a different one.")
