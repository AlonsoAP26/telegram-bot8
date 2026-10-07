from dotenv import load_dotenv
from telethon.sync import TelegramClient
import os
import asyncio


async def getListOfGroups(client):
    try:
        dialogs = await client.get_dialogs()
        groups_info = []

        for dialog in dialogs:
            if dialog.is_group or dialog.is_channel:
                entity = await client.get_entity(dialog.id)
                can_send_messages = (
                    entity.default_banned_rights is None
                    or not entity.default_banned_rights.send_messages
                )

                if can_send_messages:
                    group_info = {
                        "group_id": dialog.id,
                        "group_name": dialog.title,
                    }
                    groups_info.append(group_info)

        return groups_info

    except Exception as e:
        print(e)
        return []


async def getMessagesFromGroup(client, group_id):
    try:
        all_messages = []

        async for message in client.iter_messages(group_id):
            try:
                all_messages.append(message)
            except:
                pass

        return all_messages

    except Exception as e:
        print(e)
        return []


async def logUserBot():
    load_dotenv()

    api_id = int(os.getenv("API_ID"))
    api_hash = os.getenv("API_HASH")
    phone_number = os.getenv("PHONENUMBER")

    session_name = "bot_spammer"

    client = TelegramClient(session_name, api_id, api_hash)
    await client.connect()

    if not await client.is_user_authorized():
        await client.send_code_request(phone_number)
        await client.sign_in(
            phone_number,
            input("Ingrese el código de verificación: ")
        )

    await client.send_message(
        os.getenv("LOGS_CHANNEL"),
        "<b>Bot encendido</b>",
        parse_mode="HTML"
    )

    spammer_group = int(os.getenv("SPAMMER_GROUP"))

    while True:
        if not client.is_connected():
            print("Reconectando a Telegram...")
            try:
                await client.connect()
            except Exception as e:
                print(f"No se pudo reconectar: {e}")
                await asyncio.sleep(30)
                continue

        groups_info = await getListOfGroups(client)
        messages_list = await getMessagesFromGroup(client, spammer_group)
        try:
            await client.send_message(
                "@SpamEsteban",
                f"<b>CANTIDAD DE MENSAJES CONSEGUIDOS PARA PUBLICAR</b> <code>{len(messages_list)-1}</code>",
                parse_mode="HTML",
            )
        except:
            pass

        try:
            for i in groups_info:
                if i["group_name"] not in ["Peru Sin limites","PERU SIN LIMITES"]:

                    j = 0

                    for message_spam in messages_list:
                        j += 1
                        resultado = True

                        try:
                            await client.send_message(
                                i["group_id"],
                                message_spam
                            )

                        except Exception as error:
                            await client.send_message(
                                os.getenv("LOGS_CHANNEL"),
                                f"<b>Error enviando mensajes a {i['group_id']}</b> "
                                f"<code>{i['group_name']}</code>\n"
                                f"Causa: {error}",
                                parse_mode="HTML",
                            )
                            resultado = False

#                        if resultado:
#                            await client.send_message(
#                                os.getenv("LOGS_CHANNEL"),
#                                f"<b>Mensaje enviado a {i['group_id']}</b> - "
#                                f"<code>{i['group_name']}</code>",
#                               parse_mode="HTML",
#                            )

                        await asyncio.sleep(3)

                        if j == 3:
                            break

            await client.send_message(
                os.getenv("LOGS_CHANNEL"),
                "<b>RONDA ACABADA</b>",
                parse_mode="HTML",
            )

            await asyncio.sleep(180)

        except Exception as error:
            print(f"Error: {error}")
            print("Esperando 30 segundos para reintentar...")
            await asyncio.sleep(5)
            

    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(logUserBot())

  