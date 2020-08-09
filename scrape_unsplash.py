# src: https://medium.com/swlh/web-scraping-stock-images-using-google-selenium-and-python-8b825ba649b9
import requests
import os
import io
from PIL import Image
import hashlib
import selenium
import time
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options

def fetch_image_urls(query:str, max_links_to_fetch:int, wd:webdriver, sleep_between_interactions:int=3, verbose:bool=False):
    def scroll_to_end(wd, scroll_point):  
        wd.execute_script(f"window.scrollTo(0, {scroll_point});")
        time.sleep(sleep_between_interactions)

    # build the unsplash query
    search_url = f"https://unsplash.com/s/photos/{query}"
    # load the page
    wd.get(search_url)
    time.sleep(sleep_between_interactions)  
    
    image_urls = set()
    
    current_pixel = 0
    pixel_velocity = 1000
    pixel_acceleration = 1000
    while len(image_urls) < max_links_to_fetch:
        current_pixel += pixel_velocity
        scroll_to_end(wd, current_pixel)
        time.sleep(5)
        thumb = wd.find_elements_by_css_selector("img._2zEKz")
        time.sleep(5)
        n_unique = len(image_urls)
        for img in thumb:
            if verbose:
                print(img)
                print(img.get_attribute('src'))
            image_urls.add(img.get_attribute('src'))
            time.sleep(.5)
        n_duplicate = len(thumb)
        n_unique = len(image_urls) - n_unique
        if n_unique < n_duplicate:
            pixel_velocity += pixel_acceleration
        print(f"Duplicate: {n_duplicate}, Unique: {n_unique}")
        print(f"Found: {len(image_urls)} total search results. Extracting links...")
    return image_urls

def persist_image(folder_path:str, url:str, verbose:bool=False):
    try:
        # headers = {'User-agent': 'Chrome/64.0.3282.186'}
        headers={'User-Agent':"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36"}
        image_content = requests.get(url, headers=headers).content
        
    except Exception as e:
        print(f"ERROR - Could not download {url} - {e}")
    try:
        image_file = io.BytesIO(image_content)
        image = Image.open(image_file).convert('RGB')
        file_path = os.path.join(folder_path,hashlib.sha1(image_content).hexdigest()[:10] + '.jpg')
        with open(file_path, 'wb') as f:
            image.save(f, "PNG", quality=100)
        if verbose:
            print(f"SUCCESS - saved {url} - as {file_path}")
    except Exception as e:
        print(f"ERROR - Could not save {url} - {e}")

def search_and_download(search_term:str,driver_path:str,
                        target_path='./images-UNSPLASH',number_images=200):
    target_folder = os.path.join(target_path,'_'.join(search_term.lower().split(' ')))
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)
    options = Options()
    options.headless = True
    with webdriver.Firefox(executable_path=driver_path, options=options) as wd:
        res = fetch_image_urls(search_term, number_images, wd=wd, sleep_between_interactions=3)
        print(f'res count {len(res)}')
        for elem in res:
            persist_image(target_folder,elem)

def main():
    search_terms = ['dogs']
    driver_path = '/tmp2/cybai/scrape_google/geckodriver'
    for search_term in search_terms:
        search_and_download(search_term=search_term, driver_path=driver_path, number_images=500)

if __name__ == '__main__':
    main()