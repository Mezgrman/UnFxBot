"""
Copyright (C) 2022 Julian Metzler
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import telebot
from telebot import types
from telebot.apihelper import ApiTelegramException

import datetime
import logging
import time
import traceback

import urllib.parse

from termcolor import colored

from settings import *
from settings_secure import *

logging.basicConfig()
LOGGER = logging.getLogger("UnFxBot")
LOGGER.setLevel(logging.INFO)

"""
LISTENER
"""

def listener_console_logging(messages):
    def _readable(msg):
        if msg.content_type == 'text':
            return msg.text
        else:
            if msg.content_type is not None:
                return colored(msg.content_type.capitalize(), 'blue')
            else:
                return colored("Unknown Message Type", 'blue')

    for msg in messages:
        filtered = filter_message_incoming(msg)
        LOGGER.info("%(filtered)s[%(timestamp)s #%(mid)s %(firstname)s %(lastname)s @%(username)s #%(uid)s @ %(groupname)s #%(cid)s] %(text)s" % {
            'filtered': colored("[FILTERED]", 'red') if not filtered else "",
            'timestamp': datetime.datetime.fromtimestamp(msg.date).strftime("%d.%m.%Y %H:%M:%S"),
            'firstname': colored(msg.from_user.first_name, 'green'),
            'lastname': colored(msg.from_user.last_name, 'magenta'),
            'username': colored(msg.from_user.username, 'yellow'),
            'groupname': colored(msg.chat.title, 'red'),
            'mid': colored(str(msg.message_id), 'blue'),
            'uid': colored(str(msg.from_user.id), 'cyan'),
            'cid': colored(str(msg.chat.id), 'cyan'),
            'text': _readable(msg)
        })


bot = telebot.TeleBot(API_TOKEN, threaded = False)
bot.set_update_listener(listener_console_logging)
bot.me = bot.get_me()


"""
MESSAGE HANDLERS
"""

def filter_message_incoming(msg):
    # Discard any non-admin messages if in admin mode
    if ADMIN_ONLY and msg.chat.id != ADMIN_CID:
        return False
    # Discard messages from blacklisted users
    if msg.chat.id in BLOCKLIST:
        return False
    return True

# Handle /start
@bot.message_handler(commands = ['start'], func=filter_message_incoming)
def handle_start(msg):
    cid = msg.chat.id
    bot.send_message(cid, "Hi! Just send me a *vxtwitter* or *fxtwitter* link and I'll give you a regular twitter link. Or try /domains to see what other replacements I can make for you :)", parse_mode = 'markdown')

# Handle /domains
@bot.message_handler(commands = ['domains'], func=filter_message_incoming)
def handle_domains(msg):
    cid = msg.chat.id
    text = "The current domain replacements are:\n"
    for src, dest in ACCEPTED_DOMAINS.items():
        text += f"\n`{src}` ➔ `{dest}`"
    bot.send_message(cid, text, parse_mode = 'markdown')

# Handle URLs
@bot.message_handler(content_types=['text'], func=filter_message_incoming)
def handle_text(msg):
    cid = msg.chat.id
    try:
        parsed = urllib.parse.urlparse(msg.text)
        if parsed.netloc not in ACCEPTED_DOMAINS:
            bot.reply_to(msg, "Sorry, I don't accept this domain.")
            return
        replaced = parsed._replace(netloc=ACCEPTED_DOMAINS.get(parsed.netloc, "example.com"))
        bot.reply_to(msg, replaced.geturl())
    except:
        bot.reply_to(msg, "Sorry, I don't know what to do with this message.")

"""
RUN
"""

if __name__ == "__main__":
    exit = False
    while not exit:
        try:
            LOGGER.info("Press Ctrl-C again within one second to terminate the bot")
            time.sleep(1)
            LOGGER.info("Starting bot")
            bot.polling()
        except KeyboardInterrupt:
            LOGGER.info("Goodbye!")
            exit = True
        except:
            traceback.print_exc()
            time.sleep(10)
