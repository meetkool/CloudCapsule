import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# VNC web client details
VNC_URL = "https://app.vocon-it.com/intellij-desktop/vjufggir9ifwx3zadevhxoxkj7q2/58cHZ5Zr-aSttuu6q-tHWZ555S/?password=58cHZ5Zr-aSttuu6q-tHWZ555S&path=58cHZ5Zr-aSttuu6q-tHWZ555S/websockify&view_clip=1&resize=remote/"

def keep_vnc_active():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.get(VNC_URL)

        # Wait for the VNC canvas to load
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, "noVNC_canvas"))
        )

        while True:
            # Simulate a mouse move by executing JavaScript
            driver.execute_script("""
                var event = new MouseEvent('mousemove', {
                    'view': window,
                    'bubbles': true,
                    'cancelable': true,
                    'clientX': 100,
                    'clientY': 100
                });
                document.getElementById('noVNC_canvas').dispatchEvent(event);
            """)

            print("Kept VNC session active")

            # Wait for 14 minutes before the next action
            time.sleep(14 * 60)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    keep_vnc_active()
