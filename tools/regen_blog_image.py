#!/usr/bin/env python3
"""Regenerate blog image - no hands/fingers"""

import httpx
import base64
import os
from pathlib import Path
from dotenv import load_dotenv

project_root = Path(__file__).parent.parent
load_dotenv(project_root / '.env')

api_key = os.getenv('OPENAI_API_KEY')

print('Regenerating blog header image (abstract, no hands)...')

prompt = """Professional blog header for article about AI having names and identity.

Abstract digital art: A glowing holographic name badge or identity card floating in a cosmic space filled with soft blue and purple neural network patterns. Warm golden light emanates from the badge. Ethereal, modern, minimalist tech aesthetic.

IMPORTANT: NO HANDS, NO FINGERS, NO PEOPLE, NO FACES. Pure abstract tech visualization.

Style: Modern digital art, professional quality, wide cinematic format."""

with httpx.Client(timeout=90) as client:
    response = client.post(
        'https://api.openai.com/v1/images/generations',
        headers={
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        },
        json={
            'model': 'dall-e-3',
            'prompt': prompt,
            'n': 1,
            'size': '1792x1024',
            'quality': 'hd'
        }
    )

    if response.status_code != 200:
        print(f'ERROR: {response.status_code}')
        print(response.text)
        exit(1)

    result = response.json()
    image_url = result['data'][0]['url']
    print(f'Image generated!')

    # Download image
    img_response = client.get(image_url)

    # Save new image
    output_path = project_root / 'exports/blog-images/why-your-ai-should-have-a-name-v2.png'
    with open(output_path, 'wb') as f:
        f.write(img_response.content)
    print(f'Saved to: {output_path}')

    # Upload to WordPress
    wp_url = 'https://jaredsanborn.com'
    wp_user = os.getenv('WORDPRESS_USER')
    wp_pass = os.getenv('WORDPRESS_APP_PASSWORD')
    token = base64.b64encode(f'{wp_user}:{wp_pass}'.encode()).decode()

    print('Uploading to WordPress...')
    with open(output_path, 'rb') as f:
        img_data = f.read()

    response = client.post(
        f'{wp_url}/wp-json/wp/v2/media',
        headers={
            'Authorization': f'Basic {token}',
            'Content-Disposition': 'attachment; filename="why-your-ai-should-have-a-name-v2.png"',
            'Content-Type': 'image/png'
        },
        content=img_data
    )

    if response.status_code in [200, 201]:
        media = response.json()
        media_id = media['id']
        print(f'Uploaded! Media ID: {media_id}')

        # Update post featured image
        response = client.post(
            f'{wp_url}/wp-json/wp/v2/posts/998',
            headers={'Authorization': f'Basic {token}'},
            json={'featured_media': media_id}
        )
        if response.status_code == 200:
            print('SUCCESS: Featured image updated!')
        else:
            print(f'Error updating post: {response.status_code}')
    else:
        print(f'Upload error: {response.status_code}')
        print(response.text)
