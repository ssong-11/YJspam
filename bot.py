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
# (에러를 일으키던 contexts와 integration_types 설정을 제거하여 안정적으로 작동하게 수정했습니다)
@bot.tree.command(
    name="도배", description="원하는 메시지를 지정한 횟수만큼 반복해서 보냅니다."
)
@app_commands.describe(
    count="반복할 횟수 (1~100 사이)", message="보낼 메시지 내용"
)
async def dobai(interaction: discord.Interaction, count: int, message: str):
  # 100회 초과 제한
  if count > 100:
    await interaction.response.send_message(
        "너무 많습니다! 100 이하로 설정해주세요.", ephemeral=True
    )
    return

  # 상호작용 응답 완료 처리
  await interaction.response.send_message(
      f"'{message}' 메시지를 {count}번 보냅니다!", ephemeral=True
  )

  # 반복해서 메시지 전송 (쿨타임 방지)
  try:
    for i in range(count):
      embed = discord.Embed(
          title="📢 반복 메시지 알림",
          description=message,
          color=discord.Color.blue(),
      )
      embed.set_footer(text=f"전송 횟수: {i + 1} / {count}")

      await interaction.channel.send(embed=embed)
      await asyncio.sleep(0.6)  # 쿨타임 방지 딜레이
  except Exception as e:
    print(e)


# 4. 봇 실행
if __name__ == "__main__":
  keep_alive()
  token = os.environ.get("TOKEN")
  bot.run(token)