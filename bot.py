import asyncio
import os
from threading import Thread
import discord
from discord import app_commands
from discord.ext import commands
from flask import Flask

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


# 2. 디스코드 봇 설정 (슬래시 커맨드를 위해 tree를 함께 사용)
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)


@bot.event
async def on_ready():
  print(f'로그인 완료: {bot.user.name}')
  try:
    # 슬래시 명령어 동기화 (디스코드 서버 및 앱에 명령어 등록)
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
# 👇 DM 창 및 개인 공간에서 사용하기 위한 핵심 설정
@app_commands.contexts(
    guild=True,          # 서버 안에서 사용 허용
    dm_channel=True,     # DM 채널 안에서 사용 허용
    private_channel=True # 그룹 DM 등에서 사용 허용
)
@app_commands.integration_types(
    guild_install=True,  # 서버 설치 허용
    user_install=True    # 유저(개인 계정) 설치 허용
)
async def dobai(interaction: discord.Interaction, count: int, message: str):
  # 100회 초과 제한
  if count > 100:
    await interaction.response.send_message(
        "너무 많습니다! 100 이하로 설정해주세요.", ephemeral=True
    )
    return

  # 상호작용(Interaction) 응답을 먼저 완료 처리 (디스코드 제한 시간 대응)
  await interaction.response.send_message(
      f"'{message}' 메시지를 {count}번 보냅니다!", ephemeral=True
  )

  # 반복해서 임베드 메시지 전송 (쿨타임 방지 딜레이 포함)
  try:
    for i in range(count):
      embed = discord.Embed(
          title="📢 반복 메시지 알림",
          description=message,
          color=discord.Color.blue(),
      )
      embed.set_footer(text=f"전송 횟수: {i + 1} / {count}")

      # 명령어를 입력한 채널(서버 또는 DM)에 전송
      await interaction.channel.send(embed=embed)
      await asyncio.sleep(0.6)  # 디스코드 속도 제한(쿨타임) 방지
  except Exception as e:
    print(e)


# 4. 봇 실행 (토큰은 Render 설정에서 환경 변수로 관리)
if __name__ == "__main__":
  keep_alive()
  token = os.environ.get("TOKEN")
  bot.run(token)