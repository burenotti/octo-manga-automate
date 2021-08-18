from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message
from bot.states import NavStates
from bot.keyboards import manga_info as keyboard
from utils import include_shortname
from loader import (
    dispatcher,
    driver,
)


async def on_key_error(query: CallbackQuery, callback_data: dict):
    await query.message.delete_reply_markup()
    await query.answer("Данная кнопка устарела и больше не работает.")


@dispatcher.callback_query_handler(keyboard.action_callback_factory.filter())
@include_shortname(on_error=on_key_error)
async def info_actions(
        query: CallbackQuery,
        callback_data: dict,
        manga_shortname: str = None,
        **kwargs
):
    action = callback_data.get('action')
    manga = await driver.get_manga_info(manga_shortname)

    if action == "start_read":
        if manga.chapter_list:
            chapter_info = manga.chapter_list[0]
            url = await driver.publish_chapter(chapter_info)
            markup = await keyboard.get_in_place_keyboard(manga, 1)
            await query.message.answer(f"<a href=\"{url}\">{chapter_info.name}</a>",
                                       reply_markup=markup)

    elif action == "favourite":
        return await query.answer("Очень жаль, но это пока не работает(")

    elif action == "nav":

        return await query.message.edit_reply_markup(
            await keyboard.get_chapter_keyboard(manga)
        )


@dispatcher.callback_query_handler(keyboard.nav_callback_factory.filter(), state='*')
@include_shortname(on_error=on_key_error)
async def navigate(
        query: CallbackQuery,
        callback_data: dict,
        state: FSMContext,
        manga_shortname: str = None,
):
    action = callback_data.get('action')
    manga = await driver.get_manga_info(manga_shortname)

    if action in ("forward", "back"):
        offset = int(callback_data.get('offset')) + (10 if action == "forward" else -10)
        await query.message.edit_reply_markup(
            await keyboard.get_chapter_keyboard(manga, offset)
        )

    elif action == "cancel":
        await query.message.edit_reply_markup(
            await keyboard.get_info_keyboard(manga)
        )

    elif action == "number":
        await query.message.answer(f"Введите номер главы ({1}-{len(manga.chapter_list)})")
        await state.set_data({
            "shortname": manga_shortname,
        })
        await NavStates.ByNumber.set()

    elif action == "open":

        number = int(callback_data.get("chapter"))
        chapter = manga.chapter_list[number - 1]
        url = await driver.publish_chapter(chapter)

        markup = await keyboard.get_in_place_keyboard(manga, number)

        await query.message.answer(f"<a href=\"{url}\">{chapter.name}</a>",
                                   reply_markup=markup)


@dispatcher.message_handler(state=NavStates.ByNumber)
async def get_chapter_by_number(message: Message, state: FSMContext):
    shortname = (await state.get_data()).get("shortname")
    manga = await driver.get_manga_info(shortname)
    try:

        number = int(message.text)

    except ValueError:

        return await message.answer("Но ведь это даже не число! Давай еще раз!")

    if 1 <= number <= len(manga.chapter_list):
        chapter = manga.chapter_list[number - 1]
        url = await driver.publish_chapter(chapter)

        markup = await keyboard.get_in_place_keyboard(manga, number - 1)

        await message.answer(f"<a href=\"{url}\">{chapter.name}</a>",
                             reply_markup=markup)

        await state.finish()

    else:

        await message.answer("Нету такой главы! Давай по новой!")


@dispatcher.callback_query_handler(keyboard.in_place_callback_factory.filter())
@include_shortname(on_error=on_key_error)
async def in_place(
        query: CallbackQuery,
        callback_data: dict,
        manga_shortname: str,
        **kwargs
):
    action = callback_data.get('action')
    current_chapter = int(callback_data.get('chapter'))
    manga = await driver.get_manga_info(manga_shortname)

    if action == "next":
        next_chapter = manga.chapter_list[current_chapter]
        url = await driver.publish_chapter(next_chapter)

        markup = await keyboard.get_in_place_keyboard(manga, next_chapter.number)

        await query.message.answer(f"<a href=\"{url}\">{next_chapter.name}</a>",
                                   reply_markup=markup)
