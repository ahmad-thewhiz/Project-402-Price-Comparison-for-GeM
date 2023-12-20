import requests
from bs4 import BeautifulSoup
from urllib.parse import quote

def get_flipkart_price(product_url):
    try:
        # Send a GET request to the Flipkart product page
        response = requests.get(product_url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the HTML content of the page using BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find the div with the specified class
            price_div = soup.find('div', class_='_30jeq3 _16Jk6d')

            # Check if the div is found
            if price_div:
                # Extract and return the price text
                return price_div.text
            else:
                return "Price not found on the page. Please check the class and div selector."

        else:
            return "None"

    except Exception as e:
        return "None"

def search_flipkart(product_name):
    # Format the product name for the URL
    formatted_product_name = quote(product_name)

    # Construct the search URL
    search_url = f"https://www.flipkart.com/search?q={formatted_product_name}"

    try:
        # Send a GET request to the Flipkart search page
        response = requests.get(search_url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the HTML content of the page using BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find the first product link
            product_link = soup.find('a', class_='_1fQZEK')

            # Check if a product link is found
            if product_link:
                # Construct the product URL and return it
                product_url = 'https://www.flipkart.com' + product_link.get('href')
                return product_url
            else:
                return "No products found. Please check the product name."

        else:
            return "None"

    except Exception as e:
        return "None"
    
    
# Take input product name from the user
# product_name = input("Enter the product name: ")
# product_url = search_flipkart(product_name)

# # Use the product URL to get the price
# price = get_flipkart_price(product_url)

# print(f"The URL of the product is: {product_url}")
# print(f"The price of the product is: {price}")

def flipkart_price(product_name: str):
    product_url = search_flipkart(product_name)
    price = get_flipkart_price(product_url)
    output_details = {
        "productName": product_name,
        "productURL": product_url,
        "productPrice": price
    }
    return output_details