import os
import random
import re

import aiohttp as aiohttp

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
                for sublink in re.findall('href=\"([a-zA-Z0-9.-]*)\"', text, re.IGNORECASE):
                    if '.' not in sublink or sublink.endswith('.txt'):
                        await write_sentences_file(f'{url}/{sublink}', session, f)
            else:
                text = ''.join(re.findall('[a-zA-Z0-9 "]*', text.lower().strip()))
                while '  ' in text:
                    text = text.replace('  ', ' ')
                f.write(text)
                f.write(' ')
        except Exception as e:
            print(e)


cached_sentences = None


def sentences() -> [str, ...]:
    global cached_sentences
    if cached_sentences is None:
        with open('sentences.txt') as f:
            cached_sentences = f.read().split(' ')
    return cached_sentences


hard_separators = (' ! ', ' ? ', '.\n', '...\n', ' : ', ' !\n', ' ?\n', '...  ')
soft_separators = ('. ', ', ')


async def random_sentence() -> str:
    if not os.path.exists('sentences.txt'):
        await write_sentences_file()
    length = random.randint(30, 60)
    start = random.randint(0, len(sentences()) - length)
    parts = (sentences())[start:start + length]
    sentence = ''
    for i, part in enumerate(parts):
        sentence += part
        if i == len(parts) - 1:
            sentence += '.'
        elif random.random() < 0.05:
            sentence += random.choice(hard_separators)
        elif random.random() < 0.1:
            sentence += random.choice(soft_separators)
        else:
            sentence += ' '
    fixed_sentence = ''
    for i, c in enumerate(sentence):
        if i == 0 or (i > 2 and fixed_sentence[-2] in '.?!:'):
            c = c.upper()
        fixed_sentence += c
    return fixed_sentence


if __name__ == '__main__':
    import asyncio

    loop = asyncio.new_event_loop()


    async def print_random_sentences(n: int):
        for i in range(n):
            print(await random_sentence())
            print('-' * 100)


    loop.run_until_complete(print_random_sentences(100))
