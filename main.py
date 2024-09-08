import asyncio
import io
import json
import logging
import random
import sys
from os import getenv

from aiogram import Bot, Dispatcher, html, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.filters.callback_data import CallbackData
from aiogram.types import Message, CallbackQuery
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import KeyboardBuilder
from cases import *


def load_data():
    with io.open('data.json', 'r', encoding="utf-8") as file:
        local_data = json.load(file)
    return local_data


TOKEN = ""  # токен указывать тут
dp = Dispatcher()
data = load_data()
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

print('by angrycat. Discord - angrycat345 \n'*3)
async def open_case(message):
    case = BaseCase()
    roll = random.randint(1, 100)
    cumulative_chance = 0

    roulette_message = await message.answer(f"Кейс открывается...")
    print(roulette_message)
    for i in range(5):
        random_item_class = random.choice(list(case.items.keys()))
        print(message.chat.id)
        try:
            await bot.edit_message_text(chat_id=message.chat.id, message_id=roulette_message.message_id,
                                        text=f"Рулетка крутится... {random_item_class().name}")
        except:
            pass
        await asyncio.sleep(1)

    get_fragments = random.randint(case.min_fragments, case.max_fragments)
    winning_item = 0
    for item_class, chance in case.items.items():
        cumulative_chance += int(chance)
        if roll <= cumulative_chance:
            winning_item = item_class()
            break

    if (winning_item.name) in data[(str(message.from_user.id))]['inv']:
        cur_frag = int(data[str(message.from_user.id)]['inv'][winning_item.name]["fragments"])
        data[str(message.from_user.id)]['inv'][winning_item.name]["fragments"] = cur_frag + get_fragments
    else:
        data[str(message.from_user.id)]['inv'][winning_item.name] = {}
        data[str(message.from_user.id)]['inv'][winning_item.name]["fragments"] = get_fragments
    data[str(message.from_user.id)]['inv'][winning_item.name]["class"] = winning_item.__class__.__name__

    await bot.edit_message_text(chat_id=message.chat.id, message_id=roulette_message.message_id,
                                text=f"Вам выпали фрагменты: {winning_item.name} "
                                     f"{data[str(message.from_user.id)]['inv'][winning_item.name]['fragments']}/{winning_item.fragment}\n"
                                     f"Описание: {winning_item.description}\nРедкость: {winning_item.rare}")
    save_data(data)


def save_data(data_json):
    with io.open('data.json', 'w', encoding="utf-8") as json_file:
        json.dump(data_json, json_file, ensure_ascii=False)


@dp.callback_query()
async def craft(call):
    if call.data.startswith('craft'):
        call_item_name = call.data.split('_')[1]
        print(call_item_name)
        if call_item_name in data[str(call.from_user.id)]['inv']:
            instance = globals()[data[str(call.from_user.id)]['inv'][call_item_name]['class']]()

            cur_frag = int(data[str(call.from_user.id)]["inv"][call_item_name]["fragments"])
            cur_frag -= instance.fragment
            data[str(call.from_user.id)]["inv"][call_item_name]["fragments"] = cur_frag
            if "count" in data[str(call.from_user.id)]["inv"][call_item_name]:
                data[str(call.from_user.id)]["inv"][call_item_name]["count"] = int(
                    data[str(call.from_user.id)]["inv"][call_item_name]["count"]) + 1
            else:
                data[str(call.from_user.id)]["inv"][call_item_name]["count"] = 1

            await bot.send_message(call.from_user.id,
                                   f'Скрафчен {call_item_name}. У вас {data[str(call.from_user.id)]["inv"][call_item_name]["fragments"]}/{instance.fragment}')


async def write_inv_data(message):
    inv_classes = []
    inv_container = data[str(message.from_user.id)]['inv']
    message_str = 'Ваш инвентарь:\n'
    message_str_2 = 'Ваши фрагменты: \n'
    message_str_3 = 'Ваши активированные предметы: \n'
    inv_keys = inv_container.keys()

    variables_craft = []
    inline_kb_list = []
    for key in inv_keys:
        item_data = inv_container[key]

        test_case = globals()[item_data['class']]()
        index_iter = 0
        message_str_2 += "Фрагменты x" + str(item_data['fragments']) + f"/{test_case.fragment}" + " - "
        if test_case.fragment < int(item_data['fragments']):
            var_name = f"var_craft{index_iter}"
            exec(f"{var_name} = InlineKeyboardButton(text='Крафт {key}', callback_data='craft_{key}')")
            inline_kb_list.append([eval(var_name)])
            variables_craft.append(var_name)
            index_iter += 1
        message_str_2 += key + '\n'
        inv_classes.append(item_data)

        if 'count' in item_data:
            message_str += key + ' x' + str(item_data['count']) + '\n'

        if 'active_count' in item_data:
            message_str_3 += key + ' x' + str(item_data['active_count']) + '\n'

    inline_kb1 = InlineKeyboardMarkup(inline_keyboard=inline_kb_list)
    message_str += '\nЧтобы использовать предмет напишите "использовать название предмета"'
    await message.answer(f"{message_str}")
    await message.answer(f"{message_str_3}")
    await message.answer(f"{message_str_2}", reply_markup=inline_kb1)


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    if not data.__contains__(str(message.from_user.id)):
        data[str(message.from_user.id)] = {'bal': 0, 'inv': {}}
    kb = [
        [types.KeyboardButton(text="Клик")],
        [types.KeyboardButton(text="Баланс")],
        [types.KeyboardButton(text="Кейсы")],
        [types.KeyboardButton(text="Инвентарь")],
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

    await message.answer(f"Привет, {html.bold(message.from_user.full_name)}!", reply_markup=keyboard)
    save_data(data)


@dp.message()
async def echo_handler(message: Message) -> None:
    if message.text.lower() == 'баланс':
        await message.answer(f"Вы имеете {data[str(message.from_user.id)]['bal']}🌵!")
    elif message.text.lower() == "клик":
        randint_cactus = random.randint(1, 5)
        inv_container = data[str(message.from_user.id)]['inv']
        inv_keys = inv_container.keys()
        for key in inv_keys:
            item_data = inv_container[key]
            if 'active_count' in item_data:
                test_case = globals()[item_data['class']]()
                chance = test_case.chance
                boost = test_case.boost

                added_chance = 0
                for i in range(item_data['active_count']):
                    chance_int = random.randint(0, 100)
                    if chance_int <= chance:
                        randint_cactus += boost
                        added_chance += boost

                if added_chance > 0:
                    await message.answer(f"Добавлено {added_chance}🌵 засчет {key} x{item_data['active_count']}!")

        cur_balance = int(data[str(message.from_user.id)]['bal'])
        cur_balance += randint_cactus
        data[str(message.from_user.id)]['bal'] = cur_balance
        await message.answer(f"Вы заработали {randint_cactus}🌵")
    elif message.text.lower() == 'инвентарь':
        await write_inv_data(message)
    elif message.text.lower() == 'кейсы':
        kb = [
            [types.KeyboardButton(text="Обычный кейс")]
        ]
        keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

        await message.answer(
            f"Из этих бонусов могут выпасть различные предметы, любой ценности. Активировать можно только раз в определенное время.",
            reply_markup=keyboard)

    elif message.text.lower() == 'обычный кейс':
        await open_case(message)
    elif message.text.lower().startswith('использовать'):
        splitted_msg = message.text.split()
        del splitted_msg[0]
        name = " ".join(str(element) for element in splitted_msg)
        if name in data[str(message.from_user.id)]['inv']:
            if 'count' in data[str(message.from_user.id)]['inv'][name]:
                data[str(message.from_user.id)]['inv'][name]['count'] = int(
                    data[str(message.from_user.id)]['inv'][name]['count']) - 1

                if 'active_count' in data[str(message.from_user.id)]['inv'][name]:
                    data[str(message.from_user.id)]['inv'][name]['active_count'] = int(
                        data[str(message.from_user.id)]['inv'][name]['active_count']) + 1
                else:
                    data[str(message.from_user.id)]['inv'][name]['active_count'] = 1

                await message.answer(f"Вы активировали, {name}! Посмотреть активированные предметы можно в 'Ивентарь'")

        print(name)

    save_data(data)


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
