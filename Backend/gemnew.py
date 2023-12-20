from bs4 import BeautifulSoup
import requests

def search_product(product_name):
    search_query = product_name + ' site:https://mkp.gem.gov.in'
    google_url = "https://www.google.com/search?q=" + search_query
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    response = requests.get(google_url, headers={'User-Agent': user_agent})
    soup = BeautifulSoup(response.text, 'lxml')
    span_tag = soup.find('span', attrs={'jscontroller': 'msmzHf'})
    href = span_tag.find('a', attrs={'jsname': 'UWckNb'}).get('href') if span_tag else None

    if href:
        if href.endswith('all_sellers.html'):
            return [href]
        else:
            response = requests.get(href, headers={'User-Agent': user_agent})
            soup = BeautifulSoup(response.text, 'lxml')
            ul_tag = soup.find('ul', id='search-result-items')
            variant_image_urls = [li.find('div', class_='variant-image').find('a')['href'] for li in ul_tag.find_all('li')] if ul_tag else None
            
            if variant_image_urls:
                image_urls = ['https://mkp.gem.gov.in' + variant_image_urls[i] for i in range(min(3, len(variant_image_urls)))]
                all_sellers_urls = []
                for image_url in image_urls:
                    response = requests.get(image_url, headers={'User-Agent': user_agent})
                    soup = BeautifulSoup(response.text, 'lxml')
                    other_sellers_url = soup.find('div', class_='other-sellers-info').find('a', class_='sellers_summary')['href']
                    all_sellers_urls.append("https://mkp.gem.gov.in" + other_sellers_url)
                
                return all_sellers_urls
            else:
                return None
    else:
        return None

def scrape_data(url):
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    rows = soup.find_all('tr')
    all_sellers_data = []
    lowest_price = float('inf')
    lowest_price_seller = None

    for row in rows:
        row_data = {}
        seller_name_td = row.find('td', class_='seller-name')
        if seller_name_td:
            row_data['Seller Name'] = seller_name_td.get_text(strip=True)

        offer_price_td = row.find('td', class_='offer-price')
        if offer_price_td:
            offer_price = float(offer_price_td.get_text(strip=True).replace(',', '').replace('₹', '').strip())
            row_data['Offer Price'] = offer_price

            if offer_price < lowest_price:
                lowest_price = offer_price
                lowest_price_seller = row_data.copy()

        delivery_location_td = row.find('td', class_='delivery-locations')
        if delivery_location_td:
            row_data['Delivery Locations'] = delivery_location_td.get_text(strip=True)

        quantity_available_td = row.find('td', class_='quantity-available')
        if quantity_available_td:
            row_data['Quantity Available'] = quantity_available_td.get_text(strip=True)

        moq_td = row.find('td', class_='moq')
        if moq_td:
            row_data['MOQ'] = moq_td.get_text(strip=True)

        offer_product_td = row.find('td', class_='offer-product')
        if offer_product_td:
            row_data['Offer Product'] = offer_product_td.get_text(strip=True)

        country_origin_td = row.find('td', class_='country-of-origin')
        if country_origin_td:
            row_data['Country of Origin'] = country_origin_td.get_text(strip=True)

        all_sellers_data.append(row_data)

    return all_sellers_data, lowest_price_seller

def get_other_sellers_url(url):
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    response = requests.get(url, headers={'User-Agent': user_agent})
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    seller_header_div = soup.find('div', class_='seller-header')
    if seller_header_div:
        anchor_tag = seller_header_div.find('a')
        if anchor_tag and 'href' in anchor_tag.attrs:
            return "https://mkp.gem.gov.in" + anchor_tag['href']
    return None

def get_product_details(url):
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    response = requests.get(url, headers={'User-Agent': user_agent})
    soup = BeautifulSoup(response.text, 'lxml')
    div = soup.find('div', {'class': 'sub-section specifications'})
    param_containers = div.find_all('div', {'class': 'param-container'})
    product_details = {}
    for container in param_containers:
        key_name = container.find('span', {'class': 'key_name'}).text.strip()
        key_value = container.find('span', {'class': 'key_value'}).text.strip()
        product_details[key_name] = key_value
    return product_details

def get_product_name(url):
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    response = requests.get(url, headers={'User-Agent': user_agent})
    soup = BeautifulSoup(response.text, 'lxml')
    div = soup.find('div', {'id': 'title'})
    name = div.find('h1', {'itemprop': 'name'}).text.strip()
    brand_name = div.find('span', {'class': 'brand-name'}).text.strip()
    model = div.find('span', {'class': 'model'}).text.strip()
    return name, brand_name, model

def scrape_image_url(url):
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    response = requests.get(url, headers={'User-Agent': user_agent})
    soup = BeautifulSoup(response.text, 'lxml')
    image_span = soup.find('span', attrs={'data-src': True})
    if image_span:
        image_url = image_span['data-src']
        return image_url
    return None

def driverFunc(product_name: str):
    output_details = []
    product_urls = search_product(product_name)

    if product_urls:
        for product_url in product_urls:
            # print(f"URL Found: {product_url}")

            all_sellers_data, lowest_price_seller = scrape_data(product_url)

            if lowest_price_seller:
                # print("Lowest Price Seller Details:")
                # print(lowest_price_seller)
                lowest_offer_price = lowest_price_seller.get('Offer Price')
                # print("Lowest Offer Price:", lowest_offer_price)
            else:
                lowest_offer_price = 0

            other_sellers_url = get_other_sellers_url(product_url)
            if other_sellers_url:
                # print(f"Other Sellers URL: {other_sellers_url}")
                product_details = get_product_details(other_sellers_url)
                # print("Product Details:")
                # for key, value in product_details.items():
                #     print(f"{key}: {value}")
                product_name, brand_name, model = get_product_name(other_sellers_url)
                # print(f"Product Name: {product_name}, Brand: {brand_name}, Model: {model}")
                image_url = scrape_image_url(other_sellers_url)
                # print("Image URL:", image_url)
                product_details = {
                    'productName': product_name,
                    'brandName': brand_name,
                    'lowestPrice': lowest_offer_price,
                    'imageURL': image_url
                }
                output_details.append(product_details)
            else:
                # print("NULL")
                product_details = {
                    'productName': "None",
                    'brandName': "None",
                    'lowestPrice': "None",
                    'imageURL': "None"
                }
                output_details.append(product_details)
    else:
        # print("NULL")
        product_details = {
            'productName': "None",
            'brandName': "None",
            'lowestPrice': "None",
            'imageURL': "None"
        }
        output_details.append(product_details)

    return output_details

print(driverFunc("Gaming Laptop"))