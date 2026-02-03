import discord
from discord.ext import commands
import logging
import os
from dotenv import load_dotenv
import asyncio

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    logger.info(f'✅ 봇이 준비되었습니다: {bot.user}')

async def load_cogs():
    """Cog 로드"""
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')
            logger.info(f'✓ Loaded cog: {filename}')

async def main():
    """봇 실행"""
    async with bot:
        await load_cogs()
        token = os.getenv('DISCORD_TOKEN')
        if not token:
            logger.error('❌ DISCORD_TOKEN이 설정되지 않았습니다!')
            return
        await bot.start(token)

if __name__ == '__main__':
    asyncio.run(main())
