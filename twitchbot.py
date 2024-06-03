# twitchbot.py
import os  # for importing env vars for the bot to use
import asyncio
from twitchio.ext import commands
from riotbot import Riotbot
import requests
import json
import sys
import time

callout_dict = {}
LOLAPI = 'INSERT_YOURS'
TFTAPI = 'INSERT_YOURS'
class Twitchbot(commands.Bot):
    riot = Riotbot()

    def __init__(self):
        # Initialise our Bot with our access token, prefix and a list of channels to join on boot...
        super().__init__(token='INSERT_YOURS', prefix='!', initial_channels=['frodude7','shiphtur','froggen','midbeast','PinkWardlol','LoLWorldChampionship','HasanAbi','TrackingthePros','Lourlo','k3soju','bebe872','DhoklaLoL','Aphromoo','keanelol'])

    async def event_ready(self):
        # We are logged in and ready to chat and use commands...
        print(f'Logged in as | {self.nick}')
        print(f'User id is | {self.user_id}')

    @commands.command()
    async def hello(self, ctx: commands.Context):
        # Send a hello back!
        # Sending a reply back to the channel is easy... Below is an example.
        await ctx.send(f'Hello {ctx.author.name}!')

    @commands.command()
    async def playawayhelp(self, ctx: commands.Context):
        statement = "!lolrank [region = na,euw,eun,kr] [Account Name]"
        await ctx.send(f'' + str(statement))

    @commands.command()
    async def tftrank(self, ctx: commands.Context, region,*arg) :
        name = ''
        for i in range(len(arg)):
            if i != 0:
                name+="%20"
            name += arg[i]
        print("received: "+region+" "+name)
        statement = self.getTFTRank(region,name)
        await ctx.send(f''+str(statement))

    @commands.command()
    async def lolrank(self, ctx: commands.Context, region,*arg) :
        name = ''
        for i in range(len(arg)):
            if i != 0:
                name+="%20"
            name += arg[i]
        print("received: "+region+" "+name)
        statement = self.getLOLRank(region,name)
        await ctx.send(f''+str(statement))
        
    @commands.command()
    async def screenshot(self, ctx: commands.Context,*arg) :
        stream = asyncio.run(self.fetch_streams(,type='live'))
        print(type(stream))
        print(ctx.channel.name+" received: "+ stream)

    def getScreenshot(self,nothing):
        #?cache=TIMEINSECONDSNOW
        print("ss")
    
    async def event_message(self, message):
        # Messages with echo set to True are messages sent by the bot...
        # For now we just want to ignore them...
        if message.echo:
            return

        # Print the contents of our message to console...
        #print(message.content)

        # Since we have commands and are overriding the default `event_message`
        # We must let the bot know we want to handle and invoke our commands...
        await self.handle_commands(message)
    
    def getRegionUrl(self,region):
        url = ''
        tag = ''
        url2 = ''
        if region.lower()=='na':
            url = 'americas.api.riotgames.com'
            url2 = 'na1.api.riotgames.com'
            tag = 'NA1'
        elif region.lower()=='uen':
            url = 'europe.api.riotgames.com'
            url2 = 'eun.api.riotgames.com'
            tag = 'EUN'
        elif region.lower()=='euw':
            url = 'europe.api.riotgames.com'
            url2 = 'euw.api.riotgames.com'
            tag = 'EUW'
        else:
            url = 'asia.api.riotgames.com'
            url2 = 'kr.api.riotgames.com'
            tag = 'KR'
        return (url,url2,tag)

    def getLOLRank(self,region, name):
        summonerid = ''
        puuid = ''
        playerName = name
        url,url2, tag = self.getRegionUrl(region)
        
        #look up the puuid using game name
        endpoint = '/riot/account/v1/accounts/by-riot-id/'+ playerName+'/'+ tag #urlencode({"name": playerName})
        curl = "https://" + url + endpoint +"?api_key=" + LOLAPI
        #print(curl)
        x = requests.get(curl)
        summoner_info = json.loads(x.text)
        #print(summoner_info)
        
        for key, value in summoner_info.items():
            if key == "puuid":
                puuid = value

        #gets the summonerid to look up rank info
        endpoint2 = '/lol/summoner/v4/summoners/by-puuid/'+puuid
        curl = "https://" + url2 + endpoint2 + "?api_key=" + LOLAPI
        #print(curl)
        x = requests.get(curl)
        account_info = json.loads(x.text)
        #print(account_info)
        for key, value in account_info.items():
            if key == "id":
                summonerid = value
        
        #get ranked info for the summonerid
        endpoint3 = '/lol/league/v4/entries/by-summoner/'+summonerid
        curl = "https://" + url2 + endpoint3 + "?api_key=" + LOLAPI
        #print(curl)
        x = requests.get(curl)
        ranked_info = json.loads(x.text)
        #print(ranked_info)
        if ranked_info == []:
            return

        try:
            tier = str(ranked_info[0]["tier"])
            rank = str(ranked_info[0]["rank"])
            wins = str(ranked_info[0]["wins"])
            loss = str(ranked_info[0]["losses"])
            rate = '%.1f'%((float(wins)/(float(wins)+float(loss)))*100)
            rank_statement = ""+playerName.replace("%20"," ") +" - "+tier+" "+rank+" with "+wins+" wins "+loss+" losses ("+rate+"% winrate)"
            print("rank_statement = "+rank_statement)
            return rank_statement
        except:
            print("exception: "+str(x)+"\n"+x.text+"\n"+str(ranked_info))

    def updateDB(self, author):
        timestamp = time.time()
        timediff = 0
        for key,value in callout_dict.items():
            if key == author:
                timediff = int(round((value-timestamp).total_seconds() / 60))

        callout_dict[author]=timestamp

        if timediff <= 2:
            print("under 2 min")
        else:
            print("request too soon, try again later")
        # print the rank (call get lol rank get tft rank)

    def getTFTRank(self,region, name):

        #gets the summonerID
        playerName = name
        summonerID = ''
        endpoint = '/tft/summoner/v1/summoners/by-name/' + playerName#urlencode({"name": playerName})
        curl = "https://" + self.getRegionUrl(region) + endpoint +"?api_key=" + TFTAPI
        #print(curl)
        x = requests.get(curl)
        summoner_info = json.loads(x.text)
        #print(summoner_info)
        for key, value in summoner_info.items():
            if key == "id":
                summonerID = value
                #print("ID = "+value)

        #gets the rank info
        endpoint2 = '/tft/league/v1/entries/by-summoner/'+summonerID
        #print(curl)
        curl = "https://" + self.getRegionUrl(region) + endpoint2 + "?api_key=" + TFTAPI
        x = requests.get(curl)
        ranked_info = json.loads(x.text)
        if ranked_info == []:
            self.getMaster(summonerID)
            return

        try:
            tier = str(ranked_info[0]["tier"])
            rank = str(ranked_info[0]["rank"])
            wins = str(ranked_info[0]["wins"])
            loss = str(ranked_info[0]["losses"])
            rate = '%.1f' % ((float(wins) / (float(wins) + float(loss))) * 100)
            rank_statement = "" + playerName.replace("%20"," ") + " - " + tier + " " + rank + " with " + wins + " wins " + loss + " losses (" + rate + "% winrate)"
            print("rank_statement = " + rank_statement)
            return rank_statement
        except:
            print("exception: "+str(x)+"\n"+x.text+"\n"+str(ranked_info))

