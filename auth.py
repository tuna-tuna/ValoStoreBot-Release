import discord
import re
import asyncio
import aiohttp
import ssl
import sys
from multidict import MultiDict
from db import Database
from log import Error, TwoFATimedOut, TwoFAWrong, UsernameOrPassword

class Auth:
    def __init__(self, username=None, password=None, message=None, ctx: discord.ApplicationContext=None, bot: discord.Bot=None):
        self.username = username
        self.password = password
        self.message = message
        self.ctx = ctx
        self.bot = bot
        self.auth_error = 'Unknown'
        self.db = Database()
        self.error = Error()

    async def authenticateaiohttp(self):
        #credit: https://github.com/RumbleMike/ValorantClientAPI/blob/master/docsv2/authentication/examples/RSO_AuthFlow.py
        if self.username == None or self.password == None:
            raise
        try:
            author_id = self.ctx.author.id
            discordName = self.ctx.author.name
            sslctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
            sslctx.set_ciphers('DEFAULT@SECLEVEL=1')
            conn = aiohttp.TCPConnector(ssl=sslctx)
            session = aiohttp.ClientSession(connector=conn, headers=MultiDict({
                'Accept-Launguage': 'en-us,en;q=0.9',
                'Accept': 'application/json, text/plain, */*'
            }))
            async with session.get('https://valorant-api.com/v1/version') as r:
                r = await r.json()
                self.clientVersion = r["data"]["riotClientVersion"]
            data = {
                'client_id': 'play-valorant-web-prod',
                'nonce': '1',
                'redirect_uri': 'https://playvalorant.com/opt_in',
                'response_type': 'token id_token',
                'scope': 'account openid'
            }
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'RiotClient/51.0.0.4429735.4381201 rso-auth (Windows;10;;Professional, x64)'
            }
            await session.post('https://auth.riotgames.com/api/v1/authorization/', json=data, headers=headers)
            
            data = {
                'type': 'auth',
                'username': self.username,
                'password': self.password,
                'remember': True
            }
            async with session.put('https://auth.riotgames.com/api/v1/authorization/', json=data, headers=headers) as r:
                data = await r.json()
                #print(data)
            if data['type'] == 'auth':
                self.auth_error = 'UNPW'
            elif data['type'] == 'multifactor':
                if self.message != None and self.bot != None and self.ctx is not None:
                    self.auth_error = '2FA'
                    await self.message.edit('**Please Enter 2FA Code.**')
                    try:
                        respond_message = await self.bot.wait_for(event="message", check = lambda msg: msg.author == self.ctx.user and msg.channel == self.ctx.channel, timeout = 90)
                        twofacode: str = respond_message.content
                    except asyncio.TimeoutError:
                        self.auth_error = '2FA Code timeout.'
                        raise
                    #print(respond_message)
                    data = {
                        "type": "multifactor",
                        "code": twofacode,
                        "rememberDevice": True
                    }
                    print(data)
                    await self.message.edit('Working...')
                    await respond_message.delete()
                    async with session.put('https://auth.riotgames.com/api/v1/authorization/', json=data, headers=headers) as r:
                        data = await r.json()
                        #print(data)
                        for cookie in r.headers.getall('Set-Cookie'):
                            if cookie.startswith('ssid='):
                                self.ssid_cookie = cookie
                                self.db.setCookie(author_id, discordName, self.ssid_cookie)
            else:
                for cookie in r.headers.getall('Set-Cookie'):
                    if cookie.startswith('ssid='):
                        self.ssid_cookie = cookie
                        self.db.setCookie(author_id, discordName, self.ssid_cookie)
            pattern = re.compile('access_token=((?:[a-zA-Z]|\d|\.|-|_)*).*id_token=((?:[a-zA-Z]|\d|\.|-|_)*).*expires_in=(\d*)')
            data = pattern.findall(data['response']['parameters']['uri'])[0] 
            access_token = data[0]

            headers = {
                'Authorization': f'Bearer {access_token}',
            }
            async with session.post('https://entitlements.auth.riotgames.com/api/token/v1', headers=headers, json={}) as r:
                data = await r.json()
            entitlements_token = data['entitlements_token']

            async with session.post('https://auth.riotgames.com/userinfo', headers=headers, json={}) as r:
                data = await r.json()
            user_id = data['sub']
            headers['X-Riot-Entitlements-JWT'] = entitlements_token
            await session.close()
            return user_id, headers, access_token
        except Exception as e:
            await session.close()
            await self.error.onError(self.bot, sys._getframe().f_code.co_name, e, data)
            if self.auth_error == 'UNPW':
                raise UsernameOrPassword
            elif self.auth_error == '2FA':
                raise TwoFAWrong
            elif self.auth_error == '2FA code timeout.':
                raise TwoFATimedOut
            else:
                raise

    async def reauth(self, author_id: str, discordName: str):
        try:
            try:
                self.ssid_cookie = self.db.getCookie(author_id)
            except:
                raise
            ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
            ctx.set_ciphers('DEFAULT@SECLEVEL=1')
            conn = aiohttp.TCPConnector(ssl=ctx)
            session = aiohttp.ClientSession(connector=conn, headers=MultiDict({
                'Accept-Launguage': 'en-us,en;q=0.9',
                'Accept': 'application/json, text/plain, */*'
            }))
            data = {
                'client_id': "play-valorant-web-prod",
                'nonce': 1,
                'redirect_uri': "https://playvalorant.com/opt_in",
                'response_type': "token id_token",
                'scope': "account openid"
            }
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'RiotClient/51.0.0.4429735.4381201 rso-auth (Windows;10;;Professional, x64)',
                'Cookie': self.ssid_cookie
            }
            r = await session.post('https://auth.riotgames.com/api/v1/authorization', json = data, headers = headers)
            self.ssid_cookie = r.headers.getall('Set-Cookie')
            for cookie in r.headers.getall('Set-Cookie'):
                if cookie.startswith('ssid='):
                    self.ssid_cookie = cookie
                    self.db.setCookie(author_id, discordName, self.ssid_cookie)
            data = await r.json()
            pattern = re.compile('access_token=((?:[a-zA-Z]|\d|\.|-|_)*).*id_token=((?:[a-zA-Z]|\d|\.|-|_)*).*expires_in=(\d*)')
            data = pattern.findall(data['response']['parameters']['uri'])[0]
            access_token = data[0]
            headers = {
                'Authorization': f'Bearer {access_token}',
            }
            async with session.post('https://entitlements.auth.riotgames.com/api/token/v1', headers=headers, json={}) as r:
                data = await r.json()
            entitlements_token = data['entitlements_token']
            headers['X-Riot-Entitlements-JWT'] = entitlements_token

            async with session.post('https://auth.riotgames.com/userinfo', headers=headers, json={}) as r:
                data = await r.json()
            user_id = data['sub']
            await session.close()
            return user_id, headers, access_token
        except Exception as e:
            await session.close()
            await self.error.onError(self.bot, sys._getframe().f_code.co_name, e, data)
            raise Exception(e)

    async def tryAuth(self):
        try:
            user_id, headers, access_token = await self.authenticateaiohttp()
            return
        except:
            raise