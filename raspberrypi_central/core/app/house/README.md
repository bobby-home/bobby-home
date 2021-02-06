# House

## Telegram bot
The system can communicate to the resident through Telegram API.
To setup this communication, you have to:
- Register your telegram bot api token.
- Register the chat_id's that will receive messages.

### Create your Telegram Bot
Please check the [telegram bot documentation](https://core.telegram.org/bots), so every information is up to date.

Basically, you have to:

1) Start a conversation with "BotFather"
2) Create a new bot, by sending to him this message: `/newbot` 
3) Tada! Get your token *("HTTP Api")* and save it in the admin.

### Get chat id's
Of course you do not want that everyone can have access to your bot to manage your house and get information about it!


To restrict access, the telegram bot will only send messages and accept messages from `chad_id` that are saved to the database.

To get this information, it can be a little bit tricky, so follow this:

1) With your telegram account, join a conversation with your bot previously created.
2) Go to `https://api.telegram.org/bot<yourtoken>/getUpdates`. You will have the information in `chat.id`, copy it and go to the admin to save it.
3) If you cannot see your chat id, remove your bot from the chat and add it back. Resend the previous request and you will see the chat id.

Voilà!
