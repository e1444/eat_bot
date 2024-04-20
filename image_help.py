import requests
from constants import *

def search_images(query):
    try:
        # Google Custom Search API endpoint
        endpoint = "https://www.googleapis.com/customsearch/v1"
        
        # Your Google Custom Search Engine ID
        cx = GOOGLE_CSE_ID
        
        # Your Google API Key
        api_key = GOOGLE_API_KEY
        
        # Parameters for the API request
        params = {
            "q": query,
            "cx": cx,
            "searchType": "image",
            "key": api_key,
            "num": 1,  # Number of results to return
        }
        
        # Send a GET request to the API
        response = requests.get(endpoint, params=params)
        
        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the JSON response
            data = response.json()
            # Extract the image URL from the response
            image_url = data["items"][0]["link"]
            return image_url
        else:
            print("Failed to search for images. Status code:", response.status_code)
            return None
    except Exception as e:
        print("An error occurred while searching for images:", e)
        return None

def download_image(url):
    try:
        # Send a GET request to the image URL
        response = requests.get(url)
        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Convert the content of the response to bytes
            image_bytes = response.content
            return image_bytes
        else:
            print("Failed to download the image. Status code:", response.status_code)
            return None
    except Exception as e:
        print("An error occurred while downloading the image:", e)
        return None

def save_image(image_bytes, filename):
    try:
        # Open the file in binary write mode and write the bytes to it
        with open(filename, "wb") as f:
            f.write(image_bytes)
        print("Image saved successfully as", filename)
    except Exception as e:
        print("An error occurred while saving the image:", e)

if __name__ == "__main__":
    # Example keyword to search for an image
    keyword = "landscape"
    
    # Search for images based on the keyword
    image_url = search_images(keyword)
    
    if image_url:
        # Download the image
        image_bytes = download_image(image_url)
        
        if image_bytes:
            # Save the image to a file
            save_image(image_bytes, "downloaded_image.jpg")