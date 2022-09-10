import os
import random
import re

import aiohttp as aiohttp
import numpy as np

from config import comments_base_link


async def write_sentences_file(url: str = comments_base_link, session=None, f=None) -> None:
    print(f'downloading {url} ...')
    if session is None:
        session = aiohttp.ClientSession()
    if f is None:
        f = open('sentences.txt', 'a')

    async with session.get(url) as resp:
        try:
            text = await resp.text()
            if 'href=' in text.lower():
                for sublink in re.findall('href=\"([a-zA-Z0-9.]*)\"', text, re.IGNORECASE):
                    await write_sentences_file(f'{url}/{sublink}', session, f)
            else:
                text = ''.join(re.findall('[a-zA-Z0-9 ."]*', text.lower()))
                while '  ' in text:
                    text = text.replace('  ', ' ')
                f.write(text)
        except Exception as e:
            print(e)


cached_sentences = None


async def sentences() -> [str, ...]:
    global cached_sentences
    if cached_sentences is None:
        if not os.path.exists('sentences.txt'):
            await write_sentences_file()
        with open('sentences.txt') as f:
            cached_sentences = f.read().split(' ')
    return cached_sentences


separators = (' ! ', ' ? ', '\n', '...') + ('. ',) * 10 + (', ',) * 15 + (' ',) * 40


async def random_sentence() -> str:
    length = random.randint(30, 60)
    start = random.randint(0, len(await sentences()) - length)
    parts = (await sentences())[start:start + length]
    sep = np.random.choice(separators, length - 1)
    sentence = ''
    for i, part in enumerate(parts):
        sentence += part
        if i < length - 1:
            sentence += sep[i]
    sentence_with_mistakes = ''
    for c in sentence:
        if random.random() < 0.001:
            c += c
        if random.random() < 0.001:
            c = c[:-1] + random.choice('qwertyuiopasdfghjklzxcvbnm')
        if random.random() < 0.001:
            c = c.upper() if c.islower() else c.lower()
        if len(sentence_with_mistakes) == 0 or len(sentence_with_mistakes) > 2 and sentence_with_mistakes[
            -2] in '.?!\n':
            c = c.upper()
        sentence_with_mistakes += c

    return sentence_with_mistakes
