import asyncio
import random
from enum import Enum, auto
import pyautogui
from random_address import real_random_address

from automation import move_to, click, scroll, write, press
from images import find
from sentences import random_sentence




class State(Enum):
    MAP = auto()
    SCROLLING_DOWN = auto()
    COMMENTING = auto()
    MUST_PRESS_OK = auto()
    MOVING = auto()


class Bot:
    def __init__(self):
        self.state = State.MAP
        self.is_running = False

    @staticmethod
    async def close_menu() -> bool:
        crosses = list(find('cross'))
        if crosses:
            await click(crosses[0])
        return len(crosses) > 0

    async def run(self):
        commented = False
        starred = False
        self.is_running = True
        while self.is_running:
            print(self.state)
            match self.state:
                case State.MAP:
                    await asyncio.sleep(1)
                    pins = find('pin')
                    if pins:
                        pin = random.choice(pins)
                        await click(pin)
                        self.state = State.SCROLLING_DOWN
                    else:
                        self.state = State.MOVING

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
                                if Bot.close_menu():
                                    self.state = State.MOVING
                                break
                            await scroll(-400)

                        if not comment_buttons:
                            if Bot.close_menu():
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
                        if Bot.close_menu():
                            self.state = State.MAP

                case State.MOVING:
                    address_search_bars = list(find('address_search_bar'))
                    if address_search_bars:
                        await click(address_search_bars[0])
                        lat, long = real_random_address()['coordinates'].values()
                        await write(f'{lat}, {long}')
                        await press('enter')
                        self.state = State.MAP
                    if Bot.close_menu():
                        self.state = State.MAP

    def stop(self):
        self.is_running = False


if __name__ == '__main__':
    bot = Bot()
    try:
        asyncio.run(bot.run())
    except OSError:
        bot.stop()
        print('Ctrl Alt Del. Killing bot')

    except KeyboardInterrupt:
        bot.stop()
        print('Ctrl C. Killing bot')
