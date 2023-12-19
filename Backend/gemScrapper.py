from bs4 import BeautifulSoup
import requests

def search_product(product_name):
    search_query = product_name + ' site:https://mkp.gem.gov.in'
    google_url = "https://www.google.com/search?q=" + search_query
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    response = requests.get(google_url, headers={'User-Agent': user_agent})
    soup = BeautifulSoup(response.text, 'html.parser')
    span_tag = soup.find('span', attrs={'jscontroller': 'msmzHf'})
    href = span_tag.find('a', attrs={'jsname': 'UWckNb'}).get('href') if span_tag else None
    return href

def scrape_data(url):
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
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
            # Convert offer price to a number for comparison
            offer_price = float(offer_price_td.get_text(strip=True).replace(',', '').replace('₹', '').strip())
            row_data['Offer Price'] = offer_price

            # Check if this is the lowest price found so far
            if offer_price < lowest_price:
                lowest_price = offer_price
                lowest_price_seller = row_data.copy()

        # Other data fields
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

        # Add to the list of all seller data
        all_sellers_data.append(row_data)

    # Return both all sellers data and the lowest price seller's data
    return all_sellers_data, lowest_price_seller

def get_other_sellers_url(url):
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    response = requests.get(url, headers={'User-Agent': user_agent})
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    seller_header_div = soup.find('div', class_='seller-header')
    if seller_header_div:
        anchor_tag = seller_header_div.find('a')
        if anchor_tag and 'href' in anchor_tag.attrs:
            return "https://mkp.gem.gov.in" + anchor_tag['href']
    return None

def get_product_details(url):
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    response = requests.get(url, headers={'User-Agent': user_agent})
    soup = BeautifulSoup(response.text, 'html.parser')
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
    soup = BeautifulSoup(response.text, 'html.parser')
    div = soup.find('div', {'id': 'title'})
    name = div.find('h1', {'itemprop': 'name'}).text.strip()
    brand_name = div.find('span', {'class': 'brand-name'}).text.strip()
    model = div.find('span', {'class': 'model'}).text.strip()
    return name, brand_name, model

def driverFunc(productName: str):
    product_name = productName
    product_url = search_product(product_name)

    if product_url:
        # print(f"URL Found: {product_url}")

        # Call scrape_data and store results in two separate variables
        all_sellers_data, lowest_price_seller = scrape_data(product_url)

        # Print all sellers data
        # print("All Sellers Data:")
        # for data in all_sellers_data:
            # print(data)

        # Store and print the lowest price seller's offer price
        if lowest_price_seller:
            # print("Lowest Price Seller Details:")
            # print(lowest_price_seller)

            # Extract and store the offer price in a separate variable
            lowest_offer_price = lowest_price_seller.get('Offer Price')
            # print("Lowest Offer Price:", lowest_offer_price)
        else:
            # print("No seller data found.")
            lowest_offer_price = 0.00

        other_sellers_url = get_other_sellers_url(product_url)
        if other_sellers_url:
            # print(f"Other Sellers URL: {other_sellers_url}")
            product_details = get_product_details(other_sellers_url)
            # print("Product Details:")
            # for key, value in product_details.items():
                # print(f"{key}: {value}")
            product_name, brand_name, model = get_product_name(other_sellers_url)
            # print(f"Product Name: {product_name}, Brand: {brand_name}, Model: {model}, Loweest Price: {lowest_offer_price}")
            print(type(lowest_offer_price))
            output_details = {
                "productName": product_name, 
                "brandName": brand_name, 
                "lowestPrice": lowest_offer_price}
        else:
            output_details = {
                "productName": "None", 
                "brandName": "None", 
                "lowestPrice": 0.00}
    else:
        output_details = {
            "productName": "None", 
            "brandName": "None", 
            "lowestPrice": 0.00}
    
    return output_details

# print(driverFunc("samsung galaxy tab s6 lite"))
