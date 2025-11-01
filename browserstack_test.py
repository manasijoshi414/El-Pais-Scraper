from selenium import webdriver
from selenium.webdriver.common.by import By
import threading
import time

# BrowserStack credentials
USERNAME = "Your BrowserStack username"
ACCESS_KEY = "Your access key"

# 5 browser/device configs - each dictionary represents different devices
BROWSER_CONFIGS = [
    {
        "browserName": "Chrome",
        "browserVersion": "latest",
        "bstack:options": {"os": "Windows", "osVersion": "10", "sessionName": "El País - Chrome Desktop"},
    },
    {
        "browserName": "Firefox",
        "browserVersion": "latest",
        "bstack:options": {"os": "Windows", "osVersion": "10", "sessionName": "El País - Firefox Desktop"},
    },
    {
        "browserName": "Safari",
        "browserVersion": "latest",
        "bstack:options": {"os": "OS X", "osVersion": "Big Sur", "sessionName": "El País - Safari Desktop"},
    },
    {
        "browserName": "iPhone 12",
        "bstack:options": {"deviceName": "iPhone 12", "osVersion": "14", "realMobile": "true", "sessionName": "El País - iPhone"},
    },
    {
        "browserName": "Samsung Galaxy S21",
        "bstack:options": {"deviceName": "Samsung Galaxy S21", "osVersion": "11.0", "realMobile": "true", "sessionName": "El País - Android"},
    },
]


def run_test(config, thread_id):
    try:
        # Merge BrowserStack credentials
        bstack_options = config.get("bstack:options", {})
        bstack_options["userName"], bstack_options["accessKey"] = USERNAME, ACCESS_KEY

        # Set capabilities
        options = webdriver.ChromeOptions() #create chrome options in capability object
        for k, v in config.items():
            if k != "bstack:options":
                options.set_capability(k, v)
        options.set_capability("bstack:options", bstack_options)

        # Launch browser on BrowserStack
        driver = webdriver.Remote(
            command_executor="https://hub-cloud.browserstack.com/wd/hub",
            options=options
        )
        # Go to opinion section
        driver.get("https://elpais.com/opinion/")
        time.sleep(2)

        #verify that articles are present 
        articles = driver.find_elements(By.TAG_NAME, "article")
        status = "passed" if articles else "failed"
        reason = "Articles found successfully" if articles else "No articles found"

        driver.execute_script(
            f'browserstack_executor: {{"action":"setSessionStatus","arguments":{{"status":"{status}","reason":"{reason}"}}}}'
        )

        print(f"Thread {thread_id}: {config['browserName']} - {reason}")
        driver.quit()

    except Exception as e:
        print(f"Thread {thread_id}: {config.get('browserName', 'Unknown')} - Error: {e}")

# Running tests in parallel threads 
def run_parallel_tests():
    threads = [
        threading.Thread(target=run_test, args=(cfg, i + 1))
        for i, cfg in enumerate(BROWSER_CONFIGS)
    ]
    for t in threads:
        t.start() # start threads
    for t in threads:
        t.join() # wait for threads to finish
    print("\nAll BrowserStack tests are completed")


if __name__ == "__main__":
    print("Starting parallel tests on BrowserStack:\n")
    run_parallel_tests()
