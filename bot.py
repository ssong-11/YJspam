import asyncio
import os
from threading import Thread
import discord
from discord import app_commands
from discord.ext import commands
from Flask import Flask

# 1. 24시간 깨워두기 위한 웹서버 (Render용)
app = Flask('')


@app.route('/')
def home():
    return 'Bot is alive!'


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
    try:
        synced = await bot.tree.sync()
        print(f'슬래시 명령어 {len(synced)}개 동기화 완료')
    except Exception as e:
        print(e)


# 3. 슬래시 명령어: /도배 [반복횟수] [보낼메시지]
@bot.tree.command(
    name="도배", description="원하는 메시지를 지정한 횟수만큼 반복해서 보냅니다."
)
@app_commands.describe(
    count="반복할 횟수 (1~100 사이)", message="보낼 메시지 내용"
)
# ❌ 에러를 일으키던 contexts 데코레이터는 제거했습니다!
@app_commands.integration_types(
    guild_install=True,  # 서버 설치 허용
    user_install=True    # 내 계정(User) 설치 허용
)
async def dobai(interaction: discord.Interaction, count: int, message: str):
    # 100회 초과 제한
    if count > 100:
        await interaction.response.send_message(
            "너무 많습니다! 100 이하로 설정해주세요.", ephemeral=True
        )
        return

    # 응답 대기 상태로 변경
    await interaction.response.defer(ephemeral=True)

    # 반복해서 메시지 전송 시도
    try:
        for _ in range(count):
            await interaction.channel.send(message)
            await asyncio.sleep(0.6)  # 디스코드 속도 제한 방지
            
        # 완료 후 나에게만 몰래 완료 메시지 전송
        await interaction.followup.send(f"'{message}' 메시지를 {count}번 보냈습니다!", ephemeral=True)
        
    except Exception as e:
        print(f"에러 발생: {e}")
        await interaction.followup.send(f"메시지 전송 실패! 권한이 부족합니다: {e}", ephemeral=True)


# 4. 봇 실행
if __name__ == "__main__":
    keep_alive()
    token = os.environ.get("TOKEN")
    bot.run(token)