import asyncio
import os
import random
import re
from enum import Enum, auto

import aiohttp as aiohttp
import cv2
import numpy as np
import pyautogui
from random_address import real_random_address

generate_results = True
comments_base_link = 'http://textfiles.com/politics'


def find(template: str) -> ((int, int), ...):
    global i
    screenshot = pyautogui.screenshot()
    screenshot.save('generated/screenshot.png')
    screenshot = cv2.imread('generated/screenshot.png', 0)
    # match pin template at all position on the screenshot
    template_ = cv2.imread(f'templates/{template}.png', 0)
    w, h = template_.shape[::-1]
    res = cv2.matchTemplate(screenshot, template_, cv2.TM_CCOEFF_NORMED)
    threshold = 0.8
    loc = tuple(zip(*np.where(res >= threshold)[::-1]))
    if generate_results and len(loc) > 0:
        for pt in loc:
            cv2.rectangle(screenshot, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)
        i = 0
        while os.path.exists(f'generated/{template} {i}.png'):
            i += 1
        cv2.imwrite(f'generated/{template} {i}.png', screenshot)
    return tuple(map(lambda pt: (pt[0] + w / 2, pt[1] + h / 2), loc))


# get all 'href=\"\w+\"'  regexp in the file downloaded at http://textfiles.com/politics/CENSORSHIP/
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


async def sentences()->[str, ...]:
    global cached_sentences
    if cached_sentences is None:
        if not os.path.exists('sentences.txt'):
            await write_sentences_file()
        with open('sentences.txt') as f:
            cached_sentences = f.read().split(' ')
    return cached_sentences


separators = (' ! ', ' ? ', '\n', '...') + ('. ',) * 2 + (', ',) * 3 + (' ',) * 20


async def random_sentence()->str:
    length = random.randint(5, 30)

    start = random.randint(0, len(await sentences()) - length) if len(await sentences()) >= length else 0
    parts = (await sentences())[start:start + length] if len(await sentences()) >= length else []
    sep = np.random.choice(separators, length - 1)
    sentence = ''
    for i, part in enumerate(parts):
        sentence += part
        if i < length - 1:
            sentence += sep[i]
    sentence_with_mistakes = ''
    for c in sentence:
        if random.random() < 0.03:
            c += c
        if random.random() < 0.02:
            c = c[:-1] + random.choice('qwertyuiopasdfghjklzxcvbnm')
        if random.random() < 0.01:
            sentence_with_mistakes += ' '
        if random.random() < 0.02:
            c = c.upper()

        sentence_with_mistakes += c
    return sentence_with_mistakes


class State(Enum):
    MAP = auto()
    SELECTING_TITLE = auto()
    SCROLLING_DOWN = auto()
    COMMENTING = auto()
    MUST_PRESS_OK = auto()
    MOVING = auto()


async def move_to(p: (int, int)):
    pyautogui.moveTo(p)
    await asyncio.sleep(0.5)


async def click(p: (int, int)):
    await move_to(p)
    pyautogui.click(p)
    await asyncio.sleep(0.5)


async def scroll(delta: int):
    pyautogui.scroll(delta)
    await asyncio.sleep(0.02)


async def write(text: str):
    for c in text:
        pyautogui.press(c)
        await asyncio.sleep(0.001)
    await asyncio.sleep(0.1)


class Bot:
    def __init__(self):
        self.state = State.MAP

    async def run(self):
        commented = False
        starred = False
        while True:
            print(self.state)
            match self.state:
                case State.MAP:
                    await asyncio.sleep(1)
                    pins = find('pin')
                    if pins:
                        pin = random.choice(pins)
                        await click(pin)
                        self.state = State.SELECTING_TITLE
                    else:
                        self.state = State.MOVING

                case State.SELECTING_TITLE:
                    self.state = State.SCROLLING_DOWN

                case State.SCROLLING_DOWN:
                    menu_centers = list(find('menu_center'))
                    if menu_centers:
                        await move_to(menu_centers[0])
                        comment_buttons = []
                        for i in range(30):
                            comment_buttons = list(find('comment_button'))
                            if comment_buttons:
                                self.state = State.COMMENTING
                                await click(comment_buttons[0])
                                break
                            modify_buttons = list(find('button_modify'))
                            if modify_buttons:
                                crosses = list(find('cross'))
                                if crosses:
                                    await click(crosses[0])
                                    self.state = State.MOVING
                                break
                            await scroll(-400)

                        if not comment_buttons:
                            crosses = list(find('cross'))
                            if crosses:
                                await click(crosses[0])
                                self.state = State.MAP

                case State.COMMENTING:
                    stars_buttons = list(find('stars_button'))
                    if stars_buttons:
                        await click(random.choice(stars_buttons))
                        starred = True
                    commenting_text_box = list(find('commenting_text_box'))
                    if commenting_text_box:
                        await click(commenting_text_box[0])
                        sentence = await random_sentence()
                        print(sentence)
                        await write(sentence)  # todo randomize message
                        commented = True
                    publish_button = list(find('publish_button'))
                    if publish_button and commented and starred:
                        await click(publish_button[0])
                        self.state = State.MUST_PRESS_OK

                case State.MUST_PRESS_OK:
                    ok_buttons = list(find('ok_button'))
                    if ok_buttons:
                        await click(ok_buttons[0])
                        crosses = list(find('cross'))
                        if crosses:
                            await click(crosses[0])
                            self.state = State.MAP

                case State.MOVING:
                    address_search_bars = list(find('address_search_bar'))
                    if address_search_bars:
                        await click(address_search_bars[0])
                        lat, long = real_random_address()['coordinates'].values()
                        await write(f'{lat}, {long}')
                        pyautogui.press('enter')
                        await asyncio.sleep(1)
                        self.state = State.MAP
                    crosses = list(find('cross'))
                    if crosses:
                        await click(crosses[0])
                        self.state = State.MAP

if __name__ == '__main__':
    asyncio.run(Bot().run())
