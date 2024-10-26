NekoGPT2
===
NekoGPT2 is a neko girl! Modified from the NekoGPT. Welcome to chat with me!
It has now been switched to using the official API
You can also set up this discord robot by yourself.


Invite me: https://nekogpt.cocomine.cc/ <br>
*Power by GPT-4o-mini*
<hr>

# How to deploy

## Docker (Recommended)
### Step 1: Install docker
Check out the official website: https://docs.docker.com/engine/install/
To install docker on your server.

### Step 2: Install docker-compose Plugin
Check out the official website: https://docs.docker.com/compose/install/
To install docker-compose on your server.

### Step 3: Download docker-compose-tamplate
Download [docker-compose-tamplate](/docker-compose-tamplate.yml) into your server.

### Step 3: Edit docker-compose-tamplate
Open the **docker-compose-tamplate** file and edit following content.
```YAML
environment:
    # Please fill up following environment variables
    - BOT_NAME=NekoGPT
    - DISCORD_TOKEN=
    - SPEECH_KEY=
    - SPEECH_REGION=
    - OPENAI_BASE_URL=default
    - OPENAI_API_KEY=
    - OPENAI_ASSISTANT_ID=
    - SQL_DRIVER=sqlite3
    - MYSQL_HOST=
    - MYSQL_PORT=
    - MYSQL_USER=
    - MYSQL_PASSWORD=
    - MYSQL_DATABASE=
    - DISCORD_CUSTOM_LOADING_EMOJI=
```

3.1: Fill in the corresponding information in the file.
- BOT_NAME: 
  - The name of your bot.
- DISCORD_TOKEN: 
  - Your discord bot token. 
  - You can get it from https://discord.com/developers/applications
  - Learn more: https://discordpy.readthedocs.io/en/stable/discord.html
- SPEECH_KEY and SPEECH_REGION: 
  - Are used to convert text to speech.
  - You can get it from https://speech.microsoft.com/portal
- OPENAI_BASE_URL:
  - (Optional) The base URL of the OpenAI API. Default is `https://api.openai.com/v1`.
- OPENAI_API_KEY: Your OpenAI API key.
  - You can get it from https://platform.openai.com/api-keys
- OPENAI_ASSISTANT_ID:
  - Fill in your own assistant ID. If you do not fill it in, it will be automatically created for you.
- SQL_DRIVER: 
  - The database driver used by the bot. The default is `sqlite3`.
- MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE:
  - The information of the MySQL database. If you use MySQL, fill in this information.
- DISCORD_CUSTOM_LOADING_EMOJI:
  - (Optional) The custom emoji used when the bot is loading. Default is `🔄`.

3.2: Replace **volumes** with the path to the folder where you want to store the database.
```YAML
volumes:
    # Replace this with the path to the folder where you want to store the database.
    - /path/to/your/data/folder:/database
```
- Replace `/path/to/your/data/folder` with the path to the folder where you want to store the database.
- This folder will be used to store the database, so you can use it to back up the database.

### Step 4: Run docker-compose
Run the following command to start the bot.
```shell
docker-compose up -d
```

### Step 6: Invite your bot to your server
You can use the following link to invite your bot to your server.
```
https://discord.com/api/oauth2/authorize?client_id=YOUR_CLIENT_ID&permissions=274881562688&scope=bot
```
- Replace `YOUR_CLIENT_ID` with your bot's client ID.
- You can get it from https://discord.com/developers/applications
- Learn more: https://discordpy.readthedocs.io/en/stable/discord.html

### Step 7: Enjoy!