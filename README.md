# SysBot.py

A trade bot built for Pokémon Brilliant Diamond and Shining Pearl. It also offers additional functions for shiny hunting (pending more being added).

## Warning

You must have a hacked nintendo switch to run this. I am not liable for any damages or bans you might get in the process of running this. Use at your own risk.

## Dependencies

- [sys-botbase](https://github.com/olliz0r/sys-botbase/releases) 2.0 or higher.

## Usage
You will need Python 3.9 or above


Ensure you have the necessary libraries by running:
`pip install -r requirements.txt`

To run the bot:
- Run App.py to generate a blank config.json
- Fill out the config
- Run App.py again

## Modes

The botType setting in the config specifies the routine the bot performs.
- Sysbot - A Trade bot that manages a queue on discord.
  * Must have the global room unlocked. 
  * Save state should be somewhere outside.
  * Use +help for the list of usable commands.
- Eggbot - An automated shiny egg hunting bot.
  * Daycare must already contain parents that can produce eggs.
  * Must be in Solaceon town.

## Support

Questions and help wanted for using the bot can come to me here

[<img src="https://discordapp.com/api/guilds/680260945666113591/widget.png?style=banner2">](https://discord.gg/Yh9hBYt)


## Credits

While this was just a little project it has been very fun to implement and wouldn't have been such a pleasure without the following people.


- [@architdate](https://github.com/architdate) for being such a wonderful inspiration and friend. Your support has always meant the world to me.

- [@SteveCookTU](https://github.com/SteveCookTU) for code reformatting and cleaning. As well as helping me test running the bot and being an amazing resource and helper.

- [@kwsch](https://github.com/kwsch) and everyone who has worked on PKHeX to make it the power house that is today with excellent reference code (especially for encryption and decryption of Pokémon data along with documentation of the structures)
