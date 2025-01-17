import discord
from discord.ext import commands

from aiogoogletrans import Translator
import json
import os
from dotenv import load_dotenv

from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "I'm alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

# Keep Alive 설정
def keep_alive():
    app = Flask('')
    @app.route('/')
    def home():
        return "I'm alive!"
    def run():
        app.run(host='0.0.0.0', port=8080)
    t = Thread(target=run)
    t.start()

keep_alive()  # 웹 서버 시작

# .env 파일 로드
load_dotenv()

# 환경 변수 가져오기
TOKEN = os.getenv("DISCORD_TOKEN")
# 번역기 초기화
translator = Translator()

# 봇 초기화
intents = discord.Intents.default()
intents.messages = True  # 메시지 이벤트 활성화
intents.message_content = True  # 메시지 내용 접근 활성화
bot = commands.Bot(command_prefix="!", intents=intents)


if os.path.exists("user_settings.json"):
    with open("user_settings.json", "r") as f:
        user_settings = {int(k): v for k, v in json.load(f).items()}
    print("json file loaded.")
else:
    print("json file not found.")
    user_settings = {}

# 구성원별 언어 설정 저장
@bot.tree.command(name="setlanguage", description="Set your preferred language.")
async def setlanguage(interaction: discord.Interaction, lang: str):
    """사용자가 선호 언어를 설정합니다."""
    user_settings[interaction.user.id] = {"preferred_lang": lang}
    with open("user_settings.json", "w") as f:
        json.dump(user_settings, f, indent=4)

    await interaction.response.send_message(f"You'll receive {lang} result", ephemeral=True)

@bot.event
async def on_ready():
    # bot.tree.clear_commands(guild=None)  # 전체 명령어 삭제
    await bot.tree.sync()               # 새 명령어 동기화
    print(f"{bot.user} is online!")


# 메시지 컨텍스트 메뉴 등록
@bot.tree.context_menu(name="번역하기")
async def translate_message(interaction: discord.Interaction, message: discord.Message):
    user_id = interaction.user.id

    # 사용자 설정 확인
    if user_id not in user_settings.keys():
        print("keys : ", user_settings.keys())
        print("user id : ", user_id)

        await interaction.response.send_message("No preferred language settings. Please register your settings first.", ephemeral=True)
        return

    settings = user_settings[user_id]
    target_lang = settings["preferred_lang"]

    # 메시지 번역
    result = await translator.translate(message.content, src="auto", dest=target_lang)

    # 에퍼멀 메시지로 번역 결과 전송
    await interaction.response.send_message(
        f"**[{message.author.display_name}]**\n원본: {message.content}\n번역: {result.text}",
        ephemeral=True
    )

# 디스코드 봇 실행
bot.run(TOKEN)
