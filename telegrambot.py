import os
import requests
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode
from aiogram.utils import executor
from dotenv import load_dotenv

# Load environment variables
TELEGRAM_API_TOKEN = "6273769089:AAHh3JBVQIedVIoeE6pReoT4jOFj3QSaoNo"
OPENAI_API_KEY = "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"

# Initialize bot and dispatcher
bot = Bot(token=TELEGRAM_API_TOKEN)
dp = Dispatcher(bot)

# DALL-E API
DALL_E_API_URL = "https://api.openai.com/v1/images/generations"
HEADERS = {"Authorization": f"Bearer {OPENAI_API_KEY}"}

async def generate_image(prompt):
    payload = {
        "model": "image-alpha-001",
        "prompt": prompt,
        "num_images": 1,
        "size": "1024x1024",
        "response_format": "url"
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(DALL_E_API_URL, json=payload, headers=HEADERS) as response:
            response_data = await response.json()
    print(response_data)  # Add this line to debug
    return response_data["data"][0]["url"]


# GPT-3 API
GPT_3_API_URL = "https://api.openai.com/v1/engines/davinci-codex/completions"
GPT_3_HEADERS = {"Authorization": f"Bearer {OPENAI_API_KEY}"}

async def generate_text(prompt):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}",
    }

    data = {
        "prompt": prompt,
        "max_tokens": 100,
        "n": 1,
        "stop": None,
        "temperature": 1,
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://api.openai.com/v1/engines/text-davinci-002/completions",  # Change the model name here
            headers=headers,
            json=data,
        ) as response:
            response_data = await response.json()
            if response.status != 200:
                raise ValueError(f"OpenAI API returned an error: {response_data}")

    if "choices" not in response_data:
        raise KeyError("The 'choices' key is missing from the OpenAI API response")

    return response_data["choices"][0]["text"].strip()



# Command handlers
@dp.message_handler(commands=["start", "help"])
async def send_welcome(message: types.Message):
    await message.reply("Welcome! Use /image to generate an image and /ask to generate a text response.")

@dp.message_handler(commands=["image"])
async def generate_image_command(message: types.Message):
    prompt = message.text[len("/image "):]
    if not prompt:
        await message.reply("Please provide a prompt for the image. Example: /image sunset")
        return
    url = await generate_image(prompt)
    await message.reply_photo(url)

@dp.message_handler(commands=["ask"])
async def generate_text_command(message: types.Message):
    prompt = message.text[len("/ask "):]
    if not prompt:
        await message.reply("Please provide a prompt for the text. Example: /ask what is AI?")
        return
    response = await generate_text(prompt)
    await message.reply(response)

if __name__ == "__main__":
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
