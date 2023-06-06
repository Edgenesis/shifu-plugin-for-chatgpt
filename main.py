# This file is the main file for the project, which is a chatgpt plugin for iot.
import io
import os

import quart
import quart_cors
import aiohttp
import time
from quart import request, Response
from PIL import Image

app = quart_cors.cors(quart.Quart(__name__), allow_origin="https://chat.openai.com")

CAMERA_URL = "http://localhost:8080"

@app.route('/image/<image_name>', methods=['GET'])
async def image(image_name):
    image_path = f'./images/{image_name}'
    return await quart.send_file(image_path, mimetype='image/jpeg')

@app.route('/capture', methods=['GET'])
async def capture():
    print("Capture request received:", request)
    async with aiohttp.ClientSession() as session:
        async with session.get(CAMERA_URL + '/capture') as resp:
            image_data = await resp.read()

            # Save the resized image data as a file
            current_time = time.strftime("snapshot-%H-%M-%S",time.localtime())
            image_name = current_time+'.jpg'
            image_path = f'./images/{image_name}'
            os.makedirs(os.path.dirname(image_path), exist_ok=True)
            with open(image_path, 'wb') as f:
                f.write(image_data)

            return quart.jsonify({'imageUrl': f'http://localhost:3333/image/{image_name}'})

@app.route('/info', methods=['GET'])
async def info():
    print("Info request received:", request)
    async with aiohttp.ClientSession() as session:
        async with session.get(CAMERA_URL + '/info') as resp:
            info_data = await resp.read()
            return Response(info_data, content_type='text/json')

@app.get("/logo.png")
async def plugin_logo():
    filename = 'logo.png'
    return await quart.send_file(filename, mimetype='image/png')

@app.get("/.well-known/ai-plugin.json")
async def plugin_manifest():
    host = request.headers['Host']
    with open("./.well-known/ai-plugin.json") as f:
        text = f.read()
        return quart.Response(text, mimetype="text/json")

@app.get("/openapi.yaml")
async def openapi_spec():
    host = request.headers['Host']
    with open("openapi.yaml") as f:
        text = f.read()
        return quart.Response(text, mimetype="text/yaml")

def main():
    app.run(debug=True, host="0.0.0.0", port=3333)

if __name__ == "__main__":
    main()
