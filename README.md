# About Lobot
[@lonabot](https://telegram.me/lonabot) on Telegram is a multipurpose bot which aims to...
be another member in your groups. He interacts with the environment, laughs, and
does plenty of other stuff (some even useful!).

This bot was originally made by [Lonami Exo](https://telegram.me/Lonami).

### Requirements
This bot requires [Requests for Python](http://docs.python-requests.org/en/latest/).
To install it by using `pip`, run `sudo -H pip install requests`.

### Technical information
This bot has been made to be compatible with Python 3.x, although it should provide a basic,
yet easily expandable, example on how Telegram bots work (and can work) so you can easily
implement it again on any other programming language, such as C#, Java, etc.

### How can I run it?
1. Make sure you have a Python interpreter (preferably 3.x compatible).
2. Create a file named `TG.token` under `/Tokens`. Inside, paste your own bot's
token (if you don't have a bot token, or even a bot, you may want to have
a look at [this](https://core.telegram.org/bots#3-how-do-i-create-a-bot)).
3. Run `python3 main.py`. Done!

### How can I add more actions or modules?
1. Head into `/src/actions/custom`, and keep `template.py` on your clipboard.
2. Enter the folder named after your action's category and paste `template.py`.
3. Rename and modify `template.py` as you wish! The next time you run Lobot, he'll know a new trick.

### How secure is this bot?
This bot is as secure as your actions are. If you want to make sure that an action is only ran by you
(i.e., an action where you list files of your computer), make sure you've added `requires_admin = True`
on your own action's `super().__init__(self)`. Also **don't forget to change who the admin is**.
You can do so by editing `/src/users/user.py`, and then changing `self.is_admin = self.id == YOUR_ID`.

Also, you **should** absolutely make sure you don't run this as root.

### Does this bot protect my privacy?
No, since it has access to all the messages, the bot owner can read them if they wish. And the bot owner
may be a bit sneaky. But hey, it's not like you're telling the bot your credit card number! Right...?
We're not to blame if you do so. Anyway, you can look at the code and see what we save and what we don't
(currently, we store user name and ID and what files were sent (not to upload the same file twice), not
the messages, [check it out](/src/database.py))

### Some actions don't work, help me! I'm panicking!
Calm, CALM! OK. Some actions require additional API keys or tokens, such as `download.py` one.
You can either not use them, or use them by getting yourself an API key.
Currently the actions that require an additional API key (and some extra steps) are the following:

#### `/utils/download.py`
First make sure that you have installed `python3-pip`. Use `sudo apt-get install python3-pip` 
if you don't have it or are unsure. Once you have it, install `youtube-dl` by using `sudo -H pip3 install youtube_dl`.
You may need to upgrade the module (simply pass `--upgrade` in the previous command).

The next thing that we need is a [YouTube Data API v3](https://developers.google.com/youtube/v3/code_samples/#python) key.
If you don't have one yet, follow these steps:s
1. Head into [Google's developers console](https://console.developers.google.com).
2. Open the menu and select _API Manager_ → _Enable API_ → _YouTube Data API_.
3. Make sure that you've set the credentials (when it asks you, what you're going to need is
access to _Public data_; this bot is _Other UI_; and since we can't know other users IPs, do nothing when it asks you).

When you _finally_ have the key, place it under `Tokens/YT.token`.
You can either restart the bot _or_ `list action download` → `enable <id>` for the changes to take effect.
