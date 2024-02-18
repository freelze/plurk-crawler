import re

url_validation_pattern = re.compile(
    r'^(?:http|ftp)s?://'
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' 
    r'localhost|'
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' 
    r'(?::\d+)?' 
    r'(?:/?|[/?]\S+)$', re.IGNORECASE)

async def url_exists(session, path):
    try:
        async with session.head(path, allow_redirects=True, timeout=10) as response:
            return response.status == 200
    except Exception as e:
        print(f"Error checking URL: {e}")
        return False
    
async def download_image(session, image_url, image_name):
    async with session.get(image_url) as response:
        with open(image_name, 'wb') as handler:
            handler.write(await response.read())  