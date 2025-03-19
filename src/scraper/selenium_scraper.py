from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import chromedriver_autoinstaller
from selenium.webdriver.chrome.options import Options
import re
import time

class SeleniumScraper:
    def __init__(self):
        try:
            # Install ChromeDriver
            chromedriver_autoinstaller.install()
            
            # Configure Chrome options
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920x1080')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            # Initialize the Chrome driver
            self.driver = webdriver.Chrome(options=options)
            self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'})
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.wait = WebDriverWait(self.driver, 10)
            print("Successfully initialized Chrome WebDriver")
            
        except Exception as e:
            print(f"Failed to initialize Selenium Scraper: {e}")
            self.driver = None
            
    def fetch_product_data(self, url, selectors):
        if not self.driver:
            print("WebDriver not initialized")
            return []
            
        try:
            print(f"Fetching with Selenium: {url}")
            self.driver.get(url)
            
            # Wait for page to load
            time.sleep(3)
            
            # Scroll to load dynamic content
            self.driver.execute_script("""
                window.scrollTo(0, document.body.scrollHeight/4);
                setTimeout(() => {
                    window.scrollTo(0, document.body.scrollHeight/2);
                }, 1000);
            """)
            time.sleep(2)
            
            wait = WebDriverWait(self.driver, 15)
            
            try:
                # Wait for any product to appear
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selectors['product_container'])))
                
                # Get all products
                products = []
                product_elements = self.driver.find_elements(By.CSS_SELECTOR, selectors['product_container'])
                
                for item in product_elements[:4]:  # Process first 4 products
                    try:
                        # Extract product details with multiple possible selectors
                        name = ''
                        for name_selector in selectors['name'].split(','):
                            try:
                                name_elem = item.find_element(By.CSS_SELECTOR, name_selector.strip())
                                name = name_elem.text.strip()
                                if name:
                                    break
                            except:
                                continue
                        
                        if not name:
                            continue
                            
                        # Extract price
                        price = ''
                        for price_selector in selectors['price'].split(','):
                            try:
                                price_elem = item.find_element(By.CSS_SELECTOR, price_selector.strip())
                                price = price_elem.text.strip()
                                if price:
                                    break
                            except:
                                continue
                                
                        if not price:
                            continue
                            
                        # Clean and convert price
                        price_value = int(re.sub(r'[^\d]', '', price))
                        if price_value == 0:
                            continue
                            
                        # Get image URL
                        image_url = ''
                        for img_selector in selectors['image'].split(','):
                            try:
                                img_elem = item.find_element(By.CSS_SELECTOR, img_selector.strip())
                                image_url = img_elem.get_attribute('src')
                                if image_url:
                                    break
                            except:
                                continue
                                
                        # Get product URL
                        product_url = ''
                        for url_selector in selectors['url'].split(','):
                            try:
                                url_elem = item.find_element(By.CSS_SELECTOR, url_selector.strip())
                                product_url = url_elem.get_attribute('href')
                                if product_url:
                                    break
                            except:
                                continue
                        
                        if not product_url:
                            continue
                            
                        # Ensure URL is absolute
                        if not product_url.startswith('http'):
                            product_url = f"https://{url.split('/')[2]}{product_url}"
                            
                        products.append({
                            'name': name,
                            'price': price_value,
                            'image': image_url,
                            'url': product_url,
                            'source': selectors['source']
                        })
                        print(f"Successfully parsed {selectors['source']} product: {name}")
                        
                    except Exception as e:
                        print(f"Error parsing individual product: {e}")
                        continue
                        
                return products
                
            except Exception as e:
                print(f"Error finding products on page: {e}")
                return []
            
        except Exception as e:
            print(f"Error in Selenium scraper: {e}")
            return []
            
    def get_page_source(self, url):
        if not self.driver:
            print("WebDriver not initialized")
            return None
            
        try:
            print(f"Fetching URL: {url}")
            self.driver.get(url)
            time.sleep(5)  # Wait for initial load
            
            # Scroll to load dynamic content
            self.driver.execute_script("""
                window.scrollTo(0, document.body.scrollHeight/4);
                setTimeout(() => {
                    window.scrollTo(0, document.body.scrollHeight/2);
                }, 1000);
            """)
            time.sleep(3)  # Wait for content to load after scroll
            
            return self.driver.page_source
            
        except Exception as e:
            print(f"Error fetching page: {e}")
            return None

    def __del__(self):
        try:
            if hasattr(self, 'driver') and self.driver:
                self.driver.quit()
        except Exception as e:
            print(f"Error closing driver: {e}") 