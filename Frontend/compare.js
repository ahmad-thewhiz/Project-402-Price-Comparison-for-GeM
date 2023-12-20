document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('searchButton').addEventListener('click', function() {
        let productName = document.getElementById('productInput').value;
        if (productName) {
            fetchPrices(productName);
        }
    });

    async function fetchPrices(productName) {
        const urls = {
            amazonPrice: `http://127.0.0.1:8000/amazonPrice/${productName}`,
            flipkartPrice: `http://127.0.0.1:8000/flipkartPrice/${productName}`,
            indiamartPrice: `http://127.0.0.1:8000/indiamartPrice/${productName}`,
            gemPrice: `http://127.0.0.1:8000/gemPrice/${productName}`
        };

        for (const [key, url] of Object.entries(urls)) {
            try {
                const response = await fetch(url, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ productName: productName })
                });
                const data = await response.json();
                displayData(key, data);
            } catch (error) {
                console.error('Error fetching data:', error);
            }
        }
    }

    function displayData(source, data) {
        if (Array.isArray(data)) {
            // Handle data as an array
            data.forEach((item, index) => {
                let card = document.getElementById(`${source}Display${index + 1}`);
                if (card) {
                    updateCardContent(source, card, item);
                }
            });
        } else {
            // Handle data as a single object
            let card = document.getElementById(`${source}Display1`);
            if (card) {
                updateCardContent(source, card, data);
            }
        }
    }
    
    // function updateCardContent(source, card, item) {
    //     // Custom formatting for each source
    //     if (source === 'amazonPrice' || source === 'flipkartPrice') {
    //         card.innerHTML = `<p>Title: ${item.Title || item.productName}<br>Price: ${item.Price || item.productPrice || item.lowestPrice}<br>Rating: ${item.Rating || 'N/A'}</p>`;
    //     } else {
    //         card.innerHTML = `<p>Product Name: ${item.productName}<br>Price: ${item.productPrice || item.lowestPrice}</p>`;
    //     }
    // }
    
    function updateCardContent(source, card, item) {
        let contentHtml = '';
    
        // Include image if available
        let imageUrlHtml = item.ImgURL ? `<img src="${item.ImgURL}" alt="${item.Title}" style="max-width: 100%; max-height: 200px;"><br>` : '';
        contentHtml += imageUrlHtml;
    
        // Common details
        contentHtml += `<p>Name: ${item.Title || item.productName}</p>`;
        contentHtml += `<p>Price: ${item.Price || item.productPrice || item.lowestPrice}</p>`;
        contentHtml += `<p>Rating: ${item.Rating || 'N/A'}</p>`;
    
        // Include a button for Amazon products if a URL is provided
        if (source === 'amazonPrice' && item.URL) {
            contentHtml += `<a href="${item.URL}" target="_blank" class="product-link-button">View Product</a>`;
        }
    
        // Include a button for Flipkart products if a URL is provided
        if (source === 'flipkartPrice' && item.URL) {
            contentHtml += `<a href="${item.URL}" target="_blank" class="product-link-button">View Product</a>`;
        }
    
        // Set the innerHTML of the card
        card.innerHTML = contentHtml;
    }
    
    
    
    

    document.getElementById('chatSubmit').addEventListener('click', function() {
        let message = document.getElementById('chatInput').value;
        if (message) {
            sendChatMessage(message);
        }
    });

    async function sendChatMessage(message) {
        const url = `http://127.0.0.1:8000/chatbot`;
        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message })
            });
            const data = await response.json();
            displayChatResponse(data);
        } catch (error) {
            console.error('Error sending chat message:', error);
        }
    }

    function displayChatResponse(data) {
        let responseDiv = document.getElementById('chatResponse');
        responseDiv.innerHTML = `<p><strong>User:</strong> ${data.message}</p><p><strong>Response:</strong> ${data.response}</p>`;
    }

    document.getElementById('increaseSize').addEventListener('click', function() {
        resizeChatModule(20); // Increase size by 20px
    });

    document.getElementById('decreaseSize').addEventListener('click', function() { // Corrected ID
        resizeChatModule(-20);
    });

    function resizeChatModule(change) {
        let chatModule = document.querySelector('.chat-module');
        let currentHeight = chatModule.offsetHeight;
        let currentWidth = chatModule.offsetWidth;
        
        let newHeight = currentHeight + change;
        let newWidth = currentWidth + change;
    
        // Ensure the chat module does not go below minimum dimensions
        newHeight = Math.max(newHeight, 100); // Minimum height: 100px
        newWidth = Math.max(newWidth, 200); // Minimum width: 200px
    
        chatModule.style.height = `${newHeight}px`;
        chatModule.style.width = `${newWidth}px`;
    }    
});