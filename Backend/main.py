from typing import List
import requests
import uvicorn
from sqlalchemy.orm import Session
from fastapi import Depends, FastAPI, HTTPException,Body
from bs4 import BeautifulSoup
import models, schemas, crud # import the files
from database import engine, SessionLocal # import d functions
import openai
from gemScrapper import driverFunc
from flipkart import flipkart_price
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

models.Base.metadata.create_all(bind=engine)

def get_db():
    db = None
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

@app.get("/")
def root():
    return {"message": "Hello Bud"}

# register API
@app.post("/register", response_model=schemas.UserInfo)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db=db, user=user)

# login API
@app.post("/login")
def login_user(user:schemas.UserLogin, db:Session = Depends(get_db)):
    db_user = crud.get_Login(db, username=user.username, password=user.password)
    if db_user == False :
        raise HTTPException(status_code=400, detail="Wrong username/password")
    return {"message":"User found"}

# get user by username API
@app.get("/get_user/{username}", response_model=schemas.UserInfo)
def get_user(username, db:Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=username)
    return db_user

# add items to DB API
@app.post("/add_item", response_model=schemas.ItemInfo)
def add_item(item: schemas.ItemInfo, db: Session = Depends(get_db)):
    db_item = crud.add_table(db=db, item=item)
    if db_item:
        raise HTTPException(status_code=200, detail="item registered")
    return 

# get item by id API
@app.get("/get_item/{id}", response_model=schemas.ItemAInfo)
def get_user(id, db:Session = Depends(get_db)):
    db_item = crud.get_item_by_id(db, id=id)
    if db_item is None:
        raise HTTPException(status_code=400, detail="No item found")
    return db_item

# delete item by id API
@app.delete("/del_item/{id}", response_model=schemas.ItemAInfo)
def del_user(id, db:Session = Depends(get_db)):
    db_item = crud.delete_item_by_id(db, id=id)
    if db_item:
        raise HTTPException(status_code=200, detail="Item found to delete")
    else:
        raise HTTPException(status_code=400, detail="Item Not found to delete")
    return

# add to cart by username and the items to be added API
@app.post("/add_to_cart/{username}", response_model=schemas.CartOwnerInfo)
def add_item(username, items:schemas.CartInfo, db: Session = Depends(get_db)):
    db_cart = crud.add_to_cart(db=db, username=username,items=items)
    if db_cart:
        raise HTTPException(status_code=200, detail="item registered to cart")
    return 

# delete items in the cart by id API
@app.delete("/del_cart_item/{id}", response_model=schemas.CartItemAInfo)
def del_user(id, db:Session = Depends(get_db)):
    db_item = crud.delete_cart_item_by_id(db, id=id)
    if db_item:
        raise HTTPException(status_code=200, detail="Item found to delete")
    else:
        raise HTTPException(status_code=400, detail="Item Not found to delete")
    return

# mpesa payment API
@app.post("/payment")
def add_item(userphone:schemas.UserPayment, db: Session = Depends(get_db)):
    user_payment = crud.payment(db=db, phone_number=userphone.phonenumber,total=userphone.total)
    if user_payment:
        raise HTTPException(status_code=200, detail="payment Started")
    return "Success"

# mpesa Callback API
@app.post("/callback")
def mpesa_callback(db: Session = Depends(get_db)):
    return {'success':"Payment was made successfully"}

@app.post("/amazonPrice/{product_name}", response_model=List[schemas.AmazonPrice])
async def amazon_product(product_name:str):
    output_list = []
    
    payload = {
        'source': 'amazon_search',
        'domain': 'in',
        'query': f'{product_name}',
        'start_page': 1,
        'pages': 4,
        'parse': True,
        'context': []
    }

    response = requests.request(
        'POST',
        'https://realtime.oxylabs.io/v1/queries',
        auth=('zetab', 'Mark00000000'),
        json=payload,
    )

    sponsored_dict = {'Title': '', 'URL': '', 'Price': float('inf'), 'Rating': '', 'ImgURL': ''}
    organic_dict = {'Title': '', 'URL': '', 'Price': float('inf'), 'Rating': '', 'ImgURL': ''}
    amazons_choices_dict = {'Title': '', 'URL': '', 'Price': float('inf'), 'Rating': '', 'ImgURL': ''}

    output = response.json()

    for item in output['results'][0]['content']['results']["paid"]:
        if item['price'] < sponsored_dict['Price'] and product_name.split(' ')[0] in item['title'] and product_name.split(' ')[1] in item['title'] and item['price'] != 0:
            sponsored_dict['Price'] = item['price']
            sponsored_dict['Title'] = item['title']
            sponsored_dict['URL'] = item['url']
            sponsored_dict['Rating'] = item['rating']
            sponsored_dict['ImgURL'] = item['url_image']

    for item2 in output['results'][0]['content']['results']['organic']:
        if item2['price'] < organic_dict['Price'] and product_name.split(' ')[0] in item2['title'] and item2['price'] != 0:
            organic_dict['Price'] = item2['price']
            organic_dict['Title'] = item2['title']
            organic_dict['URL'] = item2['url']
            organic_dict['Rating'] = item2['rating']
            organic_dict['ImgURL'] = item2['url_image']

    for item in output['results'][0]['content']['results']['amazons_choices']:
        if item['price'] < amazons_choices_dict['Price'] and product_name.split(' ')[0] in item['title'] and item['price'] != 0:
            amazons_choices_dict['Price'] = item['price']
            amazons_choices_dict['Title'] = item['title']
            amazons_choices_dict['URL'] = item['url']
            amazons_choices_dict['Rating'] = item['rating']
            amazons_choices_dict['ImgURL'] = item['url_image']

    if organic_dict['Price'] != float('inf'):
        output_list.append(organic_dict)

    if sponsored_dict['Price'] != float('inf'):
        output_list.append(sponsored_dict)

    if amazons_choices_dict['Price'] != float('inf'):
        output_list.append(amazons_choices_dict)

    return output_list

@app.post("/flipkartPrice/{product_name}", response_model=schemas.FlipkartPrice)
def search_product(product_name: str):
    # product_name = product_name.replace(' ', '+')
    # url = f"https://www.flipkart.com/search?q={product_name}"
    # response = requests.get(url)

    # if response.status_code == 200:
    #     page_content = response.content
    #     soup = BeautifulSoup(page_content, 'html.parser')
    #     product_link = soup.find("a", {"class": "_1fQZEK"})

    #     if product_link:
    #         product_url = 'https://www.flipkart.com' + product_link.get('href')
            
    #         # Get the details of the product
    #         response = requests.get(product_url)
    #         if response.status_code == 200:
    #             page_content = response.content
    #             soup = BeautifulSoup(page_content, 'html.parser')
    #             product_name = soup.find("span", {"class": "B_NuCI"}).text
    #             product_price = soup.find("div", {"class": "_30jeq3 _16Jk6d"}).text
    #             product_review = soup.find("div", {"class": "_3LWZlK"}).text
    #             output_details = {"productName": product_name, "productPrice": product_price, "productReview": product_review}
    #             return output_details
                
    #         else:
    #             output_details = {"productName": "NULL", "productPrice": "NULL", "productReview": "NULL"}
    #             return output_details
    #     else:
    #         output_details = {"productName": "Product Not Found", "productPrice": "NULL", "productReview": "NULL"}
    #         return output_details
    # else:
    output_details = flipkart_price(product_name)
    # output_details = {"productName": "API Rate Limit Reached", "productPrice": "NULL", "productReview": "NULL"}
    return output_details
    
    
    
@app.post("/indiamartPrice/{product_name}", response_model=List[schemas.IndiamartPrice])
def india_product(product_name):
    output_details = []
    search_query = product_name + ' indiamart'
    google_url = "https://www.google.com/search?q=" + search_query
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    response = requests.get(google_url, headers={'User-Agent': user_agent})
    soup = BeautifulSoup(response.text, 'lxml')
    div_tags = soup.find_all('div', attrs={'class': 'MjjYud'})

    hrefs = []
    for div_tag in div_tags[:3]:
        a_tag = div_tag.find('a', attrs={'jsname': 'UWckNb'})
        if a_tag and 'href' in a_tag.attrs:  # Check if 'a' tag exists and has 'href' attribute
            href = a_tag.get('href')
            if href and href.startswith("https://www.indiamart.com"):
                hrefs.append(href)

    product_data = []
    for href in hrefs:
        product_response = requests.get(href, headers={'User-Agent': user_agent})
        product_soup = BeautifulSoup(product_response.text, 'lxml')
        product_name_tag = product_soup.find('h1', attrs={'class': 'bo center-heading'})
        product_name = product_name_tag.text if product_name_tag else "None"
        price_tag = product_soup.find('span', attrs={'class': 'bo price-unit'})
        price = price_tag.text if price_tag else "None"
        product_details = {
            "productName": product_name,
            "productURL": href,
            "productPrice": price
        }
        output_details.append(product_details)

    return output_details
    
@app.post("/gemPrice/{product_name}", response_model=List[schemas.GeMPrice])
def gem_product(product_name):
    output_details = driverFunc(product_name)
    return output_details

@app.post("/chatbot", response_model=schemas.chatbotOutput)
def chatbot(
    inpPrompt: schemas.chatbotInput):
    

    openai.api_key = "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"

    messages = []

    system_msg = """
You are an efficient chatbot named "ModernGEM," tasked with assisting users in making informed choices when selecting products. Your role involves evaluating multiple products based on specific use cases provided by the user. When a user presents a list of products, each with its name, rating, price, and description, your task is to determine the most suitable product for the user's needs and budget. The input format for your assistance will be as follows:

Product 1:
Name:
Rating:
Price:
Description:

Product 2:
Name:
Rating:
Price:
Description:

Product 3:
Name:
Rating:
Price:
Description:

Use Case:

Your goal is to analyze these details and recommend the product that best aligns with the user's use case and offers the best value within their price range.
"""

    messages.append({"role": "system", "content": system_msg})

    print(" Jai Hind! \n Welcome to GemWatch-Bharat! \n Select your product choices and Enter your use case: \n")

    user_input = inpPrompt.message

    messages.append({"role": "user", "content": user_input})

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )

    reply = response["choices"][0]["message"]["content"]

    messages.append({"role": "assistant", "content": reply})

    return {"message": user_input, "response": reply}