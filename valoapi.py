from datetime import datetime
import discord
from auth import Auth
import aiohttp
from PIL import Image
from image import ImageEdit
import urllib3
import sys
from log import Error

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class valapi:
    def __init__(self, ctx: discord.ApplicationContext=None, bot: discord.Bot=None):
        self.session = aiohttp.ClientSession()
        self.ctx = ctx
        self.bot = bot
        self.image = Image.open('./assets/store.png')
        self.error = Error()

    async def fetch(self, endpoint='/'):
        async with self.session.get('https://pd.ap.a.pvp.net{endpoint}'.format(endpoint=endpoint), headers=self.headers) as response:
            return await response.json()

    async def fetchOffers(self):
        data = await self.fetch('/store/v2/storefront/{user_id}'.format(user_id=self.user_id))
        return data['SkinsPanelLayout']['SingleItemOffers']
    
    async def fetchPrices(self):
        data = await self.fetch('/store/v1/offers/')
        return data['Offers']

    async def fetchSkinTier(self, skinid = None):
        async with self.session.get(f'https://valorant-api.com/v1/weapons') as r:
            weaponsData = await r.json()
        tierId = ''
        for weapon in weaponsData['data']:
            for skin in weapon['skins']:
                for level in skin['levels']:
                    if level['uuid'] == skinid:
                        tierId = skin['contentTierUuid']
        async with self.session.get(f'https://valorant-api.com/v1/contenttiers') as r:
            contentTierData = await r.json()
        for tier in contentTierData['data']:
            if tier['uuid'] == tierId:
                return tier["displayIcon"]

    async def isClassic(self, skinid = None):
        async with self.session.get(f'https://valorant-api.com/v1/weapons') as r:
            weaponsData = await r.json()
        for weapon in weaponsData['data']:
            for skin in weapon['skins']:
                for level in skin['levels']:
                    if level['uuid'] == skinid:
                        if weapon['displayName'] == 'Classic':
                            return True
                        else:
                            return False

    async def fetchStore(self):
        skinid = await self.fetchOffers()
        prices = await self.fetchPrices()
        skin = []
        icon = []
        price = []
        tier = []
        classic = []
        for i in skinid:
            async with self.session.get(f'https://valorant-api.com/v1/weapons/skinlevels/{i}') as r:
                data = await r.json()
            skin.append(data['data']['displayName'])
            icon.append(data['data']['displayIcon'])
            tier.append(await self.fetchSkinTier(i))
            classic.append(await self.isClassic(i))
            for x in prices:
                if x['OfferID'] == i:
                    price.append(str(*x['Cost'].values()))
        return skin, icon, price, tier, classic

    async def start(self):
        self.message = await self.ctx.respond('Working...')
        try:
            try:
                auth = Auth(bot=self.bot)
                self.user_id, self.headers, self.access_token = await auth.reauth(self.ctx.author.id, self.ctx.author.name)
            except Exception as e:
                await self.message.edit(content='Error! Please login again!')
                raise
            embed = discord.Embed(title=f'Valorant Store', timestamp=datetime.utcnow())
            ImageClass = ImageEdit()
            try:
                filepath = ImageClass.createImage(author_id=str(self.ctx.author.id), image=self.image, skin=await self.fetchStore(), fontpath='./assets/NotoSansJP-Regular.otf')
            except:
                await self.message.edit(content='Error! Please try again later!')
                await self.session.close()
                return
            await self.session.close()
            file = discord.File(filepath)
            embed.set_image(url='attachment://' + str(self.ctx.author.id) + '_store_offers.png')
            await self.message.edit(content=None, embed=embed, file=file)
            return

        except Exception as e:
            self.message.edit(content='Sorry! Error occured! Please try again later!')
            await self.error.onError(self.bot, sys._getframe().f_code.co_name, e)
            return