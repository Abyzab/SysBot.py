# SysBot.py

A bot built for Pokémon Brilliant Diamond and Shining Pearl. It offers a persistent queue for distribution trading through discord. As well as additional functions for automated shiny hunting (pending more being added).

## Warning

You must have a hacked Nintendo Switch to run this. I am not liable for any damages or bans you might get in the process of running this. Use at your own risk.

**Ensure you have save backups of everything you care about.**

## Dependencies

- [sys-botbase](https://github.com/olliz0r/sys-botbase/releases) 2.0 or higher.

## Usage
You will need Python 3.9 or above


Ensure you have the necessary libraries by running:
`pip install -r requirements.txt`

To run the bot:
- Run `py App.py` to generate a blank config.json
- Fill out the config
- Run `py App.py` again

## Modes

The botType setting in the config specifies the routine the bot performs.
### Sysbot
A Trade bot that manages a queue on discord.
  * Must have the global room unlocked. 
  * Save state should be somewhere outside.
  * Use +help for the list of usable commands.
### Eggbot 
An automated shiny egg hunting bot.
  * Daycare must already contain parents that can produce eggs that match the eggConfig.
  * Must be in Solaceon town.
  * Send to Boxes must be set to Automatic.
  * You'll want to be on a bike unless you like running.
  * Ensure you have no eggs in your party, and that your party is full.

Within config.json you may set the conditions for the bot to stop. Example:

<img src="https://cdn.discordapp.com/attachments/733862180973314238/923365700934979604/unknown.png">

With these conditions the bot will only stop on an Egg that is Shiny, 6IV, Adamant Nature and has it's Hidden Ability. (Ability accepts 1, 2 or 4 for HA.)

The order of IVs is [HP, Atk, Def, SpA, SpD, Spe]. 

The default config provides settings that will accept any ability, nature or ivs.



## Support

Questions and help wanted for using the bot can come to me here

[<img src="https://discordapp.com/api/guilds/680260945666113591/widget.png?style=banner2">](https://discord.gg/Yh9hBYt)


## Credits

While this was just a little project it has been very fun to implement and wouldn't have been such a pleasure without the following people.


- [@architdate](https://github.com/architdate) for being such a wonderful inspiration and friend. Your support has always meant the world to me.

- [@berichan](https://github.com/berichan) for all of the help and answering my questions about Sys-botbase and being a wonderful person

- [@hp3721](https://github.com/hp3721) for constant help and support with pointers, data structures, and everything else.

- [@SteveCookTU](https://github.com/SteveCookTU) for code reformatting and cleaning. As well as helping me test running the bot and being an amazing resource and helper.

- [@kwsch](https://github.com/kwsch) and everyone who has worked on PKHeX to make it the power house that is today with excellent reference code (especially for encryption and decryption of Pokémon data along with documentation of the structures)
