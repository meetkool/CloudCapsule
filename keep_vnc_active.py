import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys


# VNC web client details
VNC_URL = "https://app.vocon-it.com/intellij-desktop/vjufggir9ifwx3zadevhxoxkj7q2/58cHZ5Zr-aSttuu6q-tHWZ555S/?password=58cHZ5Zr-aSttuu6q-tHWZ555S&path=58cHZ5Zr-aSttuu6q-tHWZ555S/websockify&view_clip=1&resize=remote/"

def keep_vnc_active():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.get(VNC_URL)

        # Wait for the VNC canvas to load
        canvas = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, "noVNC_canvas"))
        )

        while True:
            # Try multiple methods to interact
            try:
                # Method 1: JavaScript mouse event
                driver.execute_script("""
                    var event = new MouseEvent('mousemove', {
                        'view': window,
                        'bubbles': true,
                        'cancelable': true,
                        'clientX': Math.random() * window.innerWidth,
                        'clientY': Math.random() * window.innerHeight
                    });
                    document.getElementById('noVNC_canvas').dispatchEvent(event);
                """)
            except:
                pass

            try:
                # Method 2: Selenium's ActionChains
                actions = ActionChains(driver)
                actions.move_to_element_with_offset(canvas, 5, 5).perform()
            except:
                pass

            try:
                # Method 3: Send a key press
                canvas.send_keys(Keys.NULL)
            except:
                pass

            print("Attempted to keep VNC session active")

            # Wait for 14 minutes before the next action
            time.sleep(14 * 60)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()


if __name__ == "__main__":
    keep_vnc_active()
