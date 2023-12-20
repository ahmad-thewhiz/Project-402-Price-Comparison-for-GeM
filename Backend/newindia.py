from bs4 import BeautifulSoup
import requests

def search_product(product_name):
    search_query = product_name + ' indiamart'
    google_url = "https://www.google.com/search?q=" + search_query
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    response = requests.get(google_url, headers={'User-Agent': user_agent})
    soup = BeautifulSoup(response.text, 'lxml')
    div_tags = soup.find_all('div', attrs={'class': 'MjjYud'})

    hrefs = []
    for div_tag in div_tags[:3]:
        href = div_tag.find('a', attrs={'jsname': 'UWckNb'}).get('href') if div_tag else "None"
        if href and href[:25]=="https://www.indiamart.com":
            hrefs.append(href)

    product_data = []
    for href in hrefs:
        product_response = requests.get(href, headers={'User-Agent': user_agent})
        product_soup = BeautifulSoup(product_response.text, 'lxml')
        product_name_tag = product_soup.find('h1', attrs={'class': 'bo center-heading'})
        product_name = product_name_tag.text if product_name_tag else "None"
        price_tag = product_soup.find('span', attrs={'class': 'bo price-unit'})
        price = price_tag.text if price_tag else "None"
        product_data.append((product_name, href, price))

    return product_data

product_name = input("Enter a product name: ")
product_data = search_product(product_name)
for data in product_data:
    print(data)