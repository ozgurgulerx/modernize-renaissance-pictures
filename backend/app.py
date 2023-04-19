from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials
import os
from io import BytesIO
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from datetime import datetime, timedelta
from azure.storage.blob import generate_blob_sas, BlobSasPermissions
import openai
openai.api_key = "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"

app = Flask(__name__)
CORS(app)

AZURE_VISION_ENDPOINT = "XXX"
AZURE_VISION_KEY = "XXX"
AZURE_OPENAI_KEY = "XXX"
DALLE_API_ENDPOINT = "XXX"
STORAGE_ACCOUNT_NAME = "XXX"
STORAGE_ACCOUNT_KEY = "XXX"
CONTAINER_NAME = XXX"
BLOB_SERVICE = BlobServiceClient(account_url=f"https://{STORAGE_ACCOUNT_NAME}.blob.core.windows.net", credential=STORAGE_ACCOUNT_KEY)

from datetime import datetime, timedelta
from azure.storage.blob import BlobSasPermissions, generate_blob_sas, BlobServiceClient

def save_image_to_blob_storage(image_data, image_name):
    container_client = BLOB_SERVICE.get_container_client(CONTAINER_NAME)
    blob_client = container_client.get_blob_client(image_name)
    blob_client.upload_blob(image_data, overwrite=True)
    
    sas_token = generate_blob_sas(
        account_name=STORAGE_ACCOUNT_NAME,
        account_key=STORAGE_ACCOUNT_KEY,
        container_name=CONTAINER_NAME,
        blob_name=image_name,
        permissions=BlobSasPermissions(read=True),
        expiry=datetime.utcnow() + timedelta(hours=1)  # Set the token to expire in 1 hour
    )
    print(blob_client.url)
#    return f"{blob_client.url}?{sas_token}"
    return f"{blob_client.url}"

def analyze_image(image_url):
    headers = {
        'Content-Type': 'application/json',
        'Ocp-Apim-Subscription-Key': AZURE_VISION_KEY
    }
    params = {
        'visualFeatures': 'Description',
        'language': 'en'
    }
    data = {
        'url': image_url
    }
    response = requests.post(AZURE_VISION_ENDPOINT + '/vision/v3.2/analyze', headers=headers, params=params, json=data)
    
    if response.status_code != 200:
        print(response.content)  # Print the response content to help with debugging

    response.raise_for_status()
    print(response.json)
    return response.json()



def find_renaissance_painting(image_description):
    prompt = f"Find a painting that represents the following description: {image_description}"
    print(prompt)
    completions = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=100,
        n=1,
        stop=None,
        temperature=0.7
    )
    message = completions.choices[0].text.strip()
    print(message)
    return message

def generate_prompt(prompt):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=2048,
        n=1,
        stop=None,
        temperature=0.5,
    )
    print(response.choices[0].text.strip())
    return response.choices[0].text.strip()


def generate_modern_version(prompt):
    headers = {
        'Authorization': f'Bearer {AZURE_OPENAI_KEY}',
        'Content-Type': 'application/json'
    }
    data = {
        "model": "image-alpha-001",
        "prompt": prompt,
        "num_images": 1,
        "size": "1024x1024",
        "response_format": "url"
    }
    response = requests.post(DALLE_API_ENDPOINT, headers=headers, json=data)
    response.raise_for_status()
    return response.json()['data'][0]['url']

@app.route("/api/upload", methods=["POST"])
def upload_image():
    image = request.files["image"]
    image_data = image.read()
    image_name = image.filename

    image_url = save_image_to_blob_storage(image_data, image_name)
    print(image_url)
    analysis_result = analyze_image(image_url)

    # Analyze image using Azure Vision API
        # Analyze image using Azure Vision API
    image_description = analysis_result["description"]["captions"][0]["text"]
    print(image_description)

    # Find corresponding renaissance painting using Azure OpenAI
    renaissance_painting = find_renaissance_painting(image_description)

    # Generate prompt for DALL-E to create a modern version of the renaissance painting
    prompt = f"Create a modern version of the painting: {renaissance_painting}"
    print(prompt)
    dalle_prompt = generate_prompt(prompt)
    
    # Get the modern version of the renaissance painting from DALL-E API
    dalle_image_url = generate_modern_version(dalle_prompt)
    print(dalle_image_url)
    return jsonify({"dalleImage": dalle_image_url})

if __name__ == "__main__":
    app.run(debug=True)
