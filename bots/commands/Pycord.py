import json
import os
from threading import Lock
from typing import List
from discord import HTTPException, Forbidden, InvalidArgument
from discord.ext import commands


class UserQueue:

    def __init__(self, config) -> None:
        self.queue = None
        self.dir_path = f"{os.path.dirname(os.path.realpath(__file__))}/queue.json"
        self.config = config
        self.closed = config["queueClosed"]
        self.mutex = Lock()
        self.reload_queue()

    def __getitem__(self, index: int) -> str:
        self.mutex.acquire()
        item = self.queue[index]
        self.mutex.release()
        return item

    def closeQueue(self) -> None:
        self.mutex.acquire()
        self.closed = True
        self.config['queueClosed'] = True
        self.config.updateSettings()
        self.mutex.release()

    def openQueue(self) -> None:
        self.mutex.acquire()
        self.closed = False
        self.config['queueClosed'] = False
        self.config.updateSettings()
        self.mutex.release()

    def reload_queue(self) -> None:
        self.mutex.acquire()
        with open(self.dir_path, 'r') as file:
            self.queue = json.loads(file.read())
        self.mutex.release()

    def size(self) -> int:
        self.mutex.acquire()
        size = len(self.queue)
        self.mutex.release()
        return size

    def index(self, value: int) -> int:
        self.mutex.acquire()
        index = self.queue.index(value)
        self.mutex.release()
        return index

    def append(self, item: int) -> None:
        self.mutex.acquire()
        self.queue.append(item)
        self.mutex.release()
        self.updateQueue()

    def getFrontQueue(self) -> int:
        self.mutex.acquire()
        user = self.queue.pop(0)
        self.mutex.release()
        self.updateQueue()
        return user

    def __delitem__(self, index: int) -> None:
        self.mutex.acquire()
        del self.queue[index]
        self.mutex.release()
        self.updateQueue()

    def __contains__(self, item: int) -> bool:
        return item in self.queue

    def getQueue(self) -> List:
        self.mutex.acquire()
        q = self.queue.copy()
        self.mutex.release()
        return q

    def updateQueue(self) -> None:
        self.mutex.acquire()
        with open(self.dir_path, 'w') as file:
            json.dump(self.queue, file, indent=4)
        self.mutex.release()

    def clearQueue(self) -> None:
        self.mutex.acquire()
        self.queue = []
        self.mutex.release()
        self.updateQueue()


class MainCommands(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.queue = bot.queue

    @commands.command()
    async def ping(self, ctx: commands.Context) -> None:
        await ctx.send("Pong!")

    @commands.command()
    async def hi(self, ctx: commands.Context) -> None:
        await ctx.send(f"Hi ur qt {ctx.author.mention}!")

    @commands.command(aliases=['qca', 'clearall'])
    async def queue_clear_all(self, ctx: commands.Context) -> None:
        if ctx.author.id not in self.bot.config["botOwner"]:
            await ctx.send(f"You don't have permission to use this command.")
            return

        self.queue.clearQueue()
        await ctx.send(f"Cleared all from queue.")

    @commands.command(aliases=["cq"])
    async def close_queue(self, ctx: commands.Context) -> None:
        if ctx.author.id not in self.bot.config["botOwner"]:
            await ctx.send(f"You don't have permission to use this command.")
            return

        self.queue.closeQueue()
        await ctx.send(f"The Queue is now closed for entry.")

    @commands.command(aliases=["oq"])
    async def open_queue(self, ctx: commands.Context) -> None:
        if ctx.author.id not in self.bot.config["botOwner"]:
            await ctx.send(f"You don't have permission to use this command.")
            return

        self.queue.openQueue()
        await ctx.send(f"The Queue is now open for entry.")

    @commands.command(aliases=['q', 'queue'])
    async def add_queue(self, ctx: commands.Context) -> None:
        if ctx.author.id in self.queue:
            await ctx.send(f"{ctx.author.mention}, you are already in the queue.")
            return

        if self.queue.size() == self.bot.config["maxQueue"]:
            await ctx.send(f"{ctx.author.mention}, the queue is currently full.")
            return

        if self.queue.closed:
            await ctx.send(f"{ctx.author.mention}, the queue is currently closed.")
            return

        try:
            await ctx.author.send(f"Added you to the trade queue. Position: {self.queue.size()+1}")
        except (HTTPException, Forbidden, InvalidArgument):
            await ctx.send(f"Please enable direct messages to join the queue. Join failed.")
            return

        self.queue.append(ctx.author.id)

        self.bot.trigger_add_event()

        await ctx.send(f"{ctx.author.mention} has been added to the queue. Position: {self.queue.size()}.")

    @commands.command(aliases=['rq', 'lq', 'ql', 'leavequeue'])
    async def remove_queue(self, ctx: commands.Context) -> None:
        if ctx.author.id not in self.queue:
            await ctx.send(f"{ctx.author.mention}, you are not currently in the queue.")
            return

        index = self.queue.index(ctx.author.id)
        if index == 0:
            await ctx.send(f"{ctx.author.mention}, you are currently being processed. Remove failed.")
            return

        del self.queue[index]

        self.bot.trigger_remove_event()
        await ctx.send(f"{ctx.author.mention} has been removed from the queue.")

    @commands.command(aliases=['qp', 'pq'])
    async def queue_position(self, ctx: commands.Context) -> None:
        if ctx.author.id not in self.queue:
            await ctx.send(f"{ctx.author.mention}, you are not currently in the queue.")
            return

        await ctx.send(f"{ctx.author.mention} is in the queue at position {self.queue.index(ctx.author.id) + 1}.")

    @commands.command(aliases=['qs', 'queuesize'])
    async def current_queue_size(self, ctx: commands.Context) -> None:
        await ctx.send(f"The queue is currently {self.queue.size()} people.")

    @commands.command(aliases=['ds', 'sent'])
    async def sent_count(self, ctx: commands.Context) -> None:
        await ctx.send(f"The bot has sent {self.bot.settings['tradeCount']} Dittos!")

    @commands.command(aliases=['fa'])
    async def force_add(self, ctx: commands.Context, id: int) -> None:
        if ctx.author.id not in self.bot.config["botOwner"]:
            await ctx.send(f"You don't have permission to use this command.")
            return

        self.queue.append(id)

        self.bot.trigger_add_event()

        await ctx.send(f'Added user to the queue.')


def setup(bot):
    bot.add_cog(MainCommands(bot))
