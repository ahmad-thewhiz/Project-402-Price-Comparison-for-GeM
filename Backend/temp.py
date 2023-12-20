import requests
from bs4 import BeautifulSoup

def search_product(product_name):
    s = requests.Session()
    s.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    })

    product_name = product_name.replace(' ', '+')
    url = f"https://www.flipkart.com/search?q={product_name}"
    response = s.get(url)

    if response.status_code == 200:
        page_content = response.content
        soup = BeautifulSoup(page_content, 'html.parser')
        product_link = soup.find("a", {"class": "_1fQZEK"})

        if product_link:
            product_url = 'https://www.flipkart.com' + product_link.get('href')
            
            # Get the details of the product
            response = s.get(product_url)
            if response.status_code == 200:
                page_content = response.content
                soup = BeautifulSoup(page_content, 'html.parser')
                product_name = soup.find("span", {"class": "B_NuCI"}).text
                product_price = soup.find("div", {"class": "_30jeq3 _16Jk6d"}).text
                product_review = soup.find("div", {"class": "_3LWZlK"}).text
                
                return product_name, product_price, product_review
                
            else:
                return "Failed to connect to the product page."
        else:
            return "Product not found."
    else:
        return "Failed to connect to Flipkart."

product_name = input("Enter the product name: ")
print(search_product(product_name))