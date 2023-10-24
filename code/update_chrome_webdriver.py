"""
Script to update Chrome Web Driver
"""

from selenium import webdriver
import chromedriver_autoinstaller

# Check if the current version of chromedriver exists
# and if it doesn't exist, download it automatically,
# then add chromedriver to path
chromedriver_autoinstaller.install()

driver = webdriver.Chrome()
print(driver)
driver.get("http://www.python.org")
assert "Python" in driver.title
