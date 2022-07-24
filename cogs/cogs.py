import discord
import sys

from discord.commands import slash_command, Option
from discord.ext import commands
from valoapi import valapi
from db import Database
from auth import Auth
from log import Error, TwoFATimedOut, TwoFAWrong, UsernameOrPassword, Log

class valorant(commands.Cog):
    def __init__(self,bot: discord.Bot) -> None:
        self.bot = bot
        self.db = Database()
        self.error = Error()

    @slash_command(description='Login to your account')
    async def login(self, ctx: discord.ApplicationContext, username: Option(str, 'Input Username'), password: Option(str, 'Input Password')):
        await ctx.defer(ephemeral=True)
        commandName = sys._getframe().f_code.co_name
        await Log.onCommand(self.bot, ctx, commandName)
        try:
            message = await ctx.respond('Logging in...')
            auth = Auth(username=username, password=password, message=message, ctx=ctx, bot=self.bot)
            await auth.tryAuth()
            await message.edit(content='Successfully logged in!')
            return
        except UsernameOrPassword:
            await message.edit(content='Error! Username or Password may be incorrect!')
            return
        except TwoFAWrong:
            await message.edit(content='Error! 2FA code may be incorrect!')
            return
        except TwoFATimedOut:
            await message.edit(content='2FA code timed out! Please re-login!')
            return
        except Exception as e:
            await self.error.onError(self.bot, commandName, e)
            await message.edit(content='Sorry! Unknown error occured! Please try again later!')
            return

    @slash_command(description='Shows today\'s store')
    async def store(self, ctx):
        await ctx.defer(ephemeral=True)
        commandName = sys._getframe().f_code.co_name
        await Log.onCommand(self.bot, ctx, commandName)
        api = valapi(ctx)
        await api.start()

def setup(bot: discord.Bot):
    bot.add_cog(valorant(bot))
