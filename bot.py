import discord
from discord.ext import commands
import os
from flask import Flask
from threading import Thread

# 1. 24시간 깨워두기 위한 웹서버 (Render용)
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# 2. 디스코드 봇 설정
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'로그인 완료: {bot.user.name}')

# 명령어: !도배 [반복횟수] [보낼메시지]
@bot.command()
async def 도배(ctx, count: int, *, message: str):
    if count > 100:
        await ctx.send("너무 많습니다! 100 이하로 설정해주세요.")
        return
        
    for _ in range(count):
        await ctx.send(message)

# 3. 봇 실행 (토큰은 나중에 Render 설정에서 넣습니다)
if __name__ == "__main__":
    keep_alive()
    token = os.environ.get('TOKEN')
    bot.run(token)