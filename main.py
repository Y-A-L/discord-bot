import discord
from discord.ext import commands
import logging
import os
from dotenv import load_dotenv
import asyncio
from aiohttp import web

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 봇 설정
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    logger.info(f'✅ 봇이 준비되었습니다: {bot.user}')

async def load_cogs():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')
            logger.info(f'✓ Loaded cog: {filename}')

# [웹 서버 핸들러]
async def handle(request):
    return web.Response(text="I'm alive")

async def main():
    # 1. 봇 토큰 확인
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        logger.error('❌ DISCORD_TOKEN이 없습니다!')
        return

    # 2. 웹 서버 시작 (aiohttp) - 포트 8080
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    # 0.0.0.0으로 바인딩하여 외부 접속 허용
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()
    logger.info("🌍 웹 서버가 8080 포트에서 시작되었습니다.")

    # 3. 봇 실행
    async with bot:
        await load_cogs()
        await bot.start(token)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
