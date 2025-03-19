import requests
from bs4 import BeautifulSoup
import re
from .selenium_scraper import SeleniumScraper
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

class Scraper:
    def __init__(self):
        try:
            self.selenium_scraper = SeleniumScraper()
        except Exception as e:
            print(f"Failed to initialize Selenium Scraper: {e}")
            self.selenium_scraper = None
            
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }

    def clean_price(self, price_str):
        if not price_str:
            return None
        try:
            # Remove currency symbols and commas, convert to float
            price = re.sub(r'[^\d.]', '', price_str)
            return float(price) if price else None
        except:
            return None

    def fetch_flipkart_data(self, product_name):
        products = []
        try:
            search_query = product_name.replace(' ', '+')
            url = f"https://www.flipkart.com/search?q={search_query}"
            print(f"Fetching Flipkart URL: {url}")
            
            if self.selenium_scraper:
                html_content = self.selenium_scraper.get_page_source(url)
                if not html_content:
                    return []
            else:
                response = requests.get(url, headers=self.headers)
                html_content = response.text

            soup = BeautifulSoup(html_content, 'lxml')
            
            # Try multiple product container patterns
            product_containers = []
            for class_name in ['_1AtVbE col-12-12', '_4ddWXP', '_2kHMtA', '_1xHGtK _373qXS']:
                containers = soup.find_all('div', {'class': class_name})
                if containers:
                    product_containers.extend(containers)
                    print(f"Found {len(containers)} products with class {class_name}")
            
            if not product_containers:
                print("No product containers found")
                return []
            
            for container in product_containers[:5]:  # Limit to 5 products
                try:
                    # Try different product name patterns
                    name_elem = (
                        container.find('div', {'class': '_4rR01T'}) or
                        container.find('a', {'class': 's1Q9rs'}) or
                        container.find('div', {'class': '_2WkVRV'}) or
                        container.find('a', {'class': 'IRpwTa'})
                    )
                    
                    # Try different price patterns
                    price_elem = (
                        container.find('div', {'class': '_30jeq3 _1_WHN1'}) or
                        container.find('div', {'class': '_30jeq3'}) or
                        container.find('div', {'class': '_25b18c'})
                    )
                    
                    # Try different link patterns
                    link_elem = (
                        container.find('a', {'class': '_1fQZEK'}) or
                        container.find('a', {'class': '_2rpwqI'}) or
                        container.find('a', {'class': 's1Q9rs'}) or
                        container.find('a', {'class': 'IRpwTa'})
                    )
                    
                    if name_elem and price_elem and link_elem:
                        name = name_elem.text.strip()
                        price = self.clean_price(price_elem.text)
                        url = 'https://www.flipkart.com' + link_elem['href']
                        
                        # Try to get image
                        img_elem = container.find('img')
                        image = img_elem['src'] if img_elem and 'src' in img_elem.attrs else ''
                        
                        if name and price:
                            products.append({
                                'name': name,
                                'price': price,
                                'url': url,
                                'image': image
                            })
                            print(f"Found Flipkart product: {name} at ₹{price}")
                
                except Exception as e:
                    print(f"Error parsing Flipkart product: {e}")
                    continue
                
        except Exception as e:
            print(f"Error fetching Flipkart data: {e}")
        
        return products

    def fetch_amazon_data(self, product_name):
        products = []
        try:
            search_query = product_name.replace(' ', '+')
            url = f"https://www.amazon.in/s?k={search_query}"
            
            if self.selenium_scraper:
                self.selenium_scraper.driver.get(url)
                time.sleep(2)
                html_content = self.selenium_scraper.driver.page_source
            else:
                response = requests.get(url, headers=self.headers)
                html_content = response.text

            soup = BeautifulSoup(html_content, 'lxml')
            
            product_containers = soup.find_all('div', {'data-component-type': 's-search-result'})
            
            for container in product_containers[:5]:
                try:
                    name_elem = container.find('span', {'class': 'a-text-normal'})
                    price_elem = container.find('span', {'class': 'a-price-whole'})
                    url_elem = container.find('a', {'class': 'a-link-normal s-no-outline'})
                    img_elem = container.find('img', {'class': 's-image'})
                    
                    if not all([name_elem, price_elem, url_elem]):
                        continue
                        
                    name = name_elem.text.strip()
                    price = self.clean_price(price_elem.text)
                    url = 'https://www.amazon.in' + url_elem['href']
                    image = img_elem['src'] if img_elem else ''
                    
                    if name and price and url:
                        products.append({
                            'name': name,
                            'price': price,
                            'url': url,
                            'image': image
                        })
                        print(f"Found Amazon product: {name} at ₹{price}")
                except Exception as e:
                    print(f"Error parsing Amazon product: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error fetching Amazon data: {e}")
        
        return products

    def fetch_myntra_data(self, product_name):
        products = []
        try:
            search_query = product_name.replace(' ', '-')
            url = f"https://www.myntra.com/{search_query}"
            
            if self.selenium_scraper:
                self.selenium_scraper.driver.get(url)
                time.sleep(2)
                html_content = self.selenium_scraper.driver.page_source
            else:
                response = requests.get(url, headers=self.headers)
                html_content = response.text

            soup = BeautifulSoup(html_content, 'lxml')
            
            product_containers = soup.find_all('li', {'class': 'product-base'})
            
            for container in product_containers[:5]:
                try:
                    name_elem = container.find('h3', {'class': 'product-brand'})
                    price_elem = container.find('div', {'class': 'product-price'})
                    url_elem = container.find('a', {'class': 'product-base'})
                    img_elem = container.find('img', {'class': 'img-responsive'})
                    
                    if not all([name_elem, price_elem, url_elem]):
                        continue
                        
                    name = name_elem.text.strip()
                    price = self.clean_price(price_elem.text)
                    url = 'https://www.myntra.com' + url_elem['href']
                    image = img_elem['src'] if img_elem else ''
                    
                    if name and price and url:
                        products.append({
                            'name': name,
                            'price': price,
                            'url': url,
                            'image': image
                        })
                        print(f"Found Myntra product: {name} at ₹{price}")
                except Exception as e:
                    print(f"Error parsing Myntra product: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error fetching Myntra data: {e}")
        
        return products

    def fetch_product_data(self, product_name, source):
        print(f"Fetching data from {source} for: {product_name}")
        if source == 'flipkart':
            return self.fetch_flipkart_data(product_name)
        elif source == 'amazon':
            return self.fetch_amazon_data(product_name)
        elif source == 'myntra':
            return self.fetch_myntra_data(product_name)
        return []

    def fetch_price_history(self, product_url):
        # Implementation for fetching price history
        pass

    def fetch_similar_products(self, product_name):
        # Implementation for finding similar products
        pass

    def fetch_product_reviews(self, product_url):
        # Implementation for fetching product reviews
        pass

    def fetch_latest_deals(self):
        deals = []
        try:
            # Fetch Flipkart deals
            flipkart_deals = self.fetch_flipkart_latest_deals()
            if flipkart_deals:
                deals.extend(flipkart_deals)

            # Fetch Amazon deals
            amazon_deals = self.fetch_amazon_latest_deals()
            if amazon_deals:
                deals.extend(amazon_deals)

            # If no deals found, fetch some popular products instead
            if not deals:
                popular_products = self.fetch_popular_products()
                deals.extend(popular_products)

            return deals[:8]  # Return top 8 deals
        except Exception as e:
            print(f"Error fetching deals: {e}")
            return []

    def fetch_flipkart_latest_deals(self):
        try:
            url = "https://www.flipkart.com/mobile-phones-store"  # More reliable URL for deals
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            deals = []
            # Updated selectors for more reliable product finding
            deal_elements = soup.select('div._2kHMtA, div._4ddWXP, div._1AtVbE')[:8]
            
            for deal in deal_elements:
                try:
                    # Multiple selector attempts for better reliability
                    name = None
                    for name_selector in ['._4rR01T', '.s1Q9rs', '._2rpwqI']:
                        name_elem = deal.select_one(name_selector)
                        if name_elem:
                            name = name_elem.text.strip()
                            break
                    
                    if not name:
                        continue

                    # Price finding with multiple selectors
                    price_elem = deal.select_one('._30jeq3, ._1_WHN1')
                    if not price_elem:
                        continue
                    
                    price = self.normalize_price(price_elem.text)
                    if not price:
                        continue

                    # Image finding
                    image = deal.select_one('img._396cs4, img._2r_T1I')
                    if not image:
                        continue
                    image_url = image.get('src')

                    # URL finding
                    link = deal.select_one('a._1fQZEK, a._2rpwqI, a.s1Q9rs')
                    if not link:
                        continue
                    product_url = 'https://www.flipkart.com' + link['href']

                    # Discount finding (optional)
                    discount_elem = deal.select_one('._3Ay6Sb span')
                    discount = discount_elem.text.strip('% off') if discount_elem else '0'
                    
                    deals.append({
                        'name': name,
                        'price': price,
                        'image': image_url,
                        'url': product_url,
                        'discount': discount,
                        'source': 'Flipkart'
                    })
                    print(f"Found Flipkart deal: {name}")
                except Exception as e:
                    print(f"Error parsing Flipkart deal: {e}")
                    continue
                
            return deals
        except Exception as e:
            print(f"Error fetching Flipkart deals: {e}")
            return []

    def fetch_amazon_latest_deals(self):
        try:
            url = "https://www.amazon.in/gp/deals"
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            deals = []
            deal_elements = soup.select('div[data-component-type="s-search-result"]')[:8]
            
            for deal in deal_elements:
                try:
                    name_elem = deal.select_one('span.a-text-normal')
                    if not name_elem:
                        continue
                    name = name_elem.text.strip()
                    
                    price_elem = deal.select_one('span.a-price-whole')
                    if not price_elem:
                        continue
                    price = self.normalize_price(price_elem.text)
                    
                    image = deal.select_one('img.s-image')
                    image_url = image['src'] if image else None
                    
                    link = deal.select_one('a.a-link-normal')
                    if not link:
                        continue
                    product_url = 'https://www.amazon.in' + link['href']
                    
                    discount_elem = deal.select_one('span.a-text-price')
                    discount = '0'
                    if discount_elem:
                        original = self.normalize_price(discount_elem.text)
                        if original and price:
                            discount = str(int((original - price) / original * 100))
                    
                    deals.append({
                        'name': name,
                        'price': price,
                        'image': image_url,
                        'url': product_url,
                        'discount': discount,
                        'source': 'Amazon'
                    })
                except Exception as e:
                    print(f"Error parsing Amazon deal: {e}")
                    continue
            
            return deals
        except Exception as e:
            print(f"Error fetching Amazon deals: {e}")
            return []

    def fetch_popular_products(self):
        # Fallback method to fetch popular products if deals aren't available
        try:
            popular_searches = ['iphone', 'samsung', 'laptop', 'headphones']
            products = []
            
            for search in popular_searches:
                flipkart_products = self.fetch_flipkart_data(search)
                if flipkart_products:
                    products.extend(flipkart_products[:2])
                    
                amazon_products = self.fetch_amazon_data(search)
                if amazon_products:
                    products.extend(amazon_products[:2])
                    
                if len(products) >= 8:
                    break
                    
            return products[:8]
        except Exception as e:
            print(f"Error fetching popular products: {e}")
            return []

    def normalize_price(self, price_str):
        try:
            price_str = str(price_str)
            price_str = re.sub(r'[^\d.]', '', price_str)
            return float(price_str)
        except:
            return None