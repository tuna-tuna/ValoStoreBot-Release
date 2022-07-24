import os
import discord
from dotenv import load_dotenv

load_dotenv(override=True)

class Error():
    @staticmethod
    async def onError(bot: discord.Bot, funcName: str, exception: Exception, extraInfo = None, extraInfo2 = None) -> None:
        systemLogChannel = bot.get_channel(int(os.environ['DISCORD_LOG_CHANNEL']))
        embed = discord.Embed(title='Error occured', color=discord.Colour.red())
        embed.add_field(name=f'Error in {funcName}', value=f'```Traceback: \n{exception}```', inline=False)
        if extraInfo:
            embed.add_field(name=f'Extra Info', value=f'```{extraInfo}```', inline=False)
        if extraInfo2:
            embed.add_field(name=f'Extra Info 2', value=f'```{extraInfo2}```', inline=False)
        await systemLogChannel.send(embed=embed)
        return

#Original Exceptions
class TwoFAWrong(Exception):
    pass

class TwoFATimedOut(Exception):
    pass

class UsernameOrPassword(Exception):
    pass

class Log():
    @staticmethod
    async def onCommand(bot: discord.Bot, ctx: discord.ApplicationContext, funcName: str) -> None:
        systemLogChannel = bot.get_channel(int(os.environ['DISCORD_LOG_CHANNEL']))
        embed = discord.Embed(title='Command Used', color=discord.Colour.brand_green())
        author_id = ctx.author.id
        author_name = ctx.author.name
        try:
            author_nick = ctx.author.nick
        except:
            author_nick = 'None'
        try:
            author_avatar_url = ctx.author.avatar.url
        except:
            author_avatar_url = None
        try:
            guild_name = ctx.guild.name
        except:
            guild_name = 'None'
        embed.set_author(name='Command Log', icon_url=author_avatar_url)
        embed.add_field(name=funcName + ' used', value=f'```AuthorID: {author_id}\nAuthorName: {author_name}\nAuthorNick: {author_nick}\nGuildName: {guild_name}```')
        await systemLogChannel.send(embed=embed)
        return

