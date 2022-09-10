import asyncio
import os
import random
import re
from enum import Enum, auto

import aiohttp as aiohttp
import cv2
import numpy as np
import pyautogui
import pyperclip
from random_address import real_random_address

save_figs = True


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
    if save_figs and len(loc) > 0:
        for pt in loc:
            cv2.rectangle(screenshot, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)
        i = 0
        while os.path.exists(f'generated/{template} {i}.png'):
            i += 1
        cv2.imwrite(f'generated/{template} {i}.png', screenshot)
    return tuple(map(lambda pt: (pt[0] + w / 2, pt[1] + h / 2), loc))


# get all 'href=\"\w+\"'  regexp in the file downloaded at http://textfiles.com/politics/CENSORSHIP/
async def create_sentences_file() -> None:
    session = aiohttp.ClientSession()
    base_link = 'http://textfiles.com/politics/CENSORSHIP/'
    async with session.get(base_link) as resp:
        text = (await resp.text()).lower()
        sub_links = re.findall('href=\"([a-zA-Z0-9.]*)\"', text.lower())
        with open('sentences.txt', 'a') as f:
            for sub_link in sub_links:
                async with session.get(base_link + sub_link) as resp:
                    text = (await resp.text()).lower()
                    f.write(text)


cached_sentences = None


async def sentences():
    global cached_sentences
    if cached_sentences is None:
        if not os.path.exists('sentences.txt'):
            await create_sentences_file()
        with open('sentences.txt') as f:
            cached_sentences = f.read().split(' ')
    return cached_sentences


separators = (' ! ', ' ? ', '\n', '...') + ('. ',) * 2 + (', ',) * 3 + (' ',) * 12


async def random_sentence():
    length = random.randint(5, 30)
    start = random.randint(0, len(await sentences()) - length)
    parts = (await sentences())[start:start + length]
    sep = np.random.choice(separators, length - 1)
    s = ''
    for i, part in enumerate(parts):
        s += part
        if i < length - 1:
            s += sep[i]
    return s


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
    await asyncio.sleep(0.1)


async def write(text: str):
    pyperclip.copy(text)
    await asyncio.sleep(0.3)
    pyautogui.hotkey('ctrl', 'v', interval=0.15)


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
                            await scroll(-200)

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


asyncio.run(Bot().run())
