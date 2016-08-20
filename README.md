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
implement it again on any other programming language, such as C#, Java, etcetera.

### How can I run it?
1. Make sure you have a Python interpreter (preferrably 3.x compatible).
2. Create a file named `TG` under `/Tokens`. Inside, paste your own bot's
token (if you don't have a bot token, or even a bot, you may want to have
a look at [this](https://core.telegram.org/bots#3-how-do-i-create-a-bot)).
3. Run `python3 main.py`. Done!

### How can I add more actions or modules?
1. Head into `/src/actions/custom`, and keep `template.py` on your clipboard.
2. Enter the folder named after your action's category and paste `template.py`.
3. Rename and modify `template.py` as you wish! The next time you run Lobot, he'll know a new trick.

### How secure is this bot?
This bot is as secure as your actions are. If you want to make sure that an action is only ran by you
(i.e., an action where you list files of your computer), make sure you've added `self.requires_admin = True`
on your own action's `__init__(self)`. Also **don't forget to change who the admin is**.
You can do so by editing `/src/users/user.py`, and then changing `self.is_admin = self.id == YOUR_ID`.

Also, you **should** absolutely make sure you don't run this as root.

### Does this bot protect my privacy?
No, since it has access to all the messages, the bot owner can read them if they wish. And the bot owner
may be a bit sneaky. But hey, it's not like you're telling the bot your credit card number! Right...?
We're not to blame if you do so
