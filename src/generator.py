from __future__ import annotations

import requests

import dotenv
import os

from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import random
import essential_generators as eg
import wonderwords as ww
import logging

dotenv.load_dotenv()


class QuoteGenerator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.access = os.getenv("ACCESS")
        self.secret = os.getenv("SECRET")
        self.BASE = 'https://api.unsplash.com/photos'
        self.ww = ww.RandomSentence()
        self.eg = eg.DocumentGenerator()
        self.text: str = ""
        self.path: str = ""

    @property
    def headers(self):
        return {
            'Authorization': f'Client-ID {self.access}'
        }

    @staticmethod
    def get_random_font(size) -> ImageFont.FreeTypeFont:
        font_path = random.choice(os.listdir(os.path.join(os.path.dirname(__file__), '../fonts')))

        return ImageFont.truetype(os.path.join(os.path.dirname(__file__), '../fonts/', font_path), size=size)

    @staticmethod
    def get_wrapped_text(text: str, font: ImageFont.FreeTypeFont,
                         line_length: int | float) -> str:
        lines = ['']
        for word in text.split():
            line = f'{lines[-1]} {word}'.strip()
            if font.getlength(line) <= line_length:
                lines[-1] = line
            else:
                lines.append(word)
        return '\n'.join(lines)

    def get_quote(self) -> str:
        def get_from_api():
            resp = requests.get("https://randomwordgenerator.com/json/sentences.json")
            if resp.status_code == 200:
                json = resp.json()
            else:
                raise Exception(f"Error getting quote with status code {resp.status_code}")

            sentence = random.choice(json["data"])

            return sentence["sentence"]

        generators = [
            self.ww.simple_sentence,
            self.eg.sentence,
            get_from_api
        ]

        return random.choice(generators)()

    def get_photo(self) -> Image.Image:
        resp = requests.get(f"{self.BASE}/random", headers={'Authorization': f'Client-ID {self.access}'})

        download_url = resp.json()['links']['download']

        resp = requests.get(download_url)

        return Image.open(BytesIO(resp.content))

    @classmethod
    def generate_quote(cls) -> "QuoteGenerator":
        gen = cls()

        gen.logger.info("Generating quote")

        gen.logger.info("Getting photo...")
        photo = gen.get_photo()

        gen.logger.info("Getting quote...")
        quote = gen.get_quote()

        gen.logger.info("Editing image...")

        width, height = photo.size

        draw = ImageDraw.Draw(photo)
        font = gen.get_random_font(int(height / 10))
        text = gen.get_wrapped_text(quote, font, width / 1.1)

        draw.text(
            (width / 2, height / 2),
            text,
            font=font,
            fill='white',
            stroke_fill='black',
            stroke_width=5,
            anchor="mm"
        )

        gen.logger.info("Saving image...")
        path = os.path.join(os.path.dirname(__file__), '../output/', f'{quote[:10].strip()}.jpg')
        photo.save(path)

        gen.logger.info("Done!")

        gen.path = path
        gen.text = quote

        return gen


if __name__ == "__main__":
    print("Generating quote...")
    img = QuoteGenerator.generate_quote()
    print("Done!")
    print(img.path)
