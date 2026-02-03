import discord
from discord.ext import commands
import re
import random
import logging
import asyncio
from utils.perplexity_generator import PerplexityGenerator

logger = logging.getLogger(__name__)

class DiceRoller(commands.Cog):
    """D&D & 크툴루의 부름 다이스 롤러"""
    
    def __init__(self, bot):
        self.bot = bot
        self.perplexity = PerplexityGenerator()
        self.cthulhu_difficulties = {
            'regular': 1.0,
            'hard': 0.5,
            'extreme': 0.2,
        }
    
    def parse_dice_notation(self, notation: str) -> dict | None:
        """다이스 표기법 파싱"""
        notation = notation.strip('[]')
        pattern = r'^(\d+)d(\d+)([\+\-]\d+)?$'
        match = re.match(pattern, notation)
        
        if not match:
            return None
        
        num_dice = int(match.group(1))
        dice_sides = int(match.group(2))
        modifier = int(match.group(3)) if match.group(3) else 0
        
        if num_dice <= 0 or num_dice > 100:
            return None
        if dice_sides <= 0 or dice_sides > 1000:
            return None
        
        return {
            'num_dice': num_dice,
            'dice_sides': dice_sides,
            'modifier': modifier,
            'notation': notation
        }
    
    def roll_dice(self, num_dice: int, dice_sides: int) -> list:
        """주사위 굴리기"""
        return [random.randint(1, dice_sides) for _ in range(num_dice)]
    
    def determine_cthulhu_success(self, total: int, roll_list: list, dice_sides: int) -> dict:
        """크툴루의 부름 성공 판정"""
        result = {
            'total': total,
            'rolls': roll_list,
            'success_level': 'failure',
            'description': ''
        }
        
        if 1 in roll_list and len(roll_list) == 1:
            result['success_level'] = 'critical_failure'
            result['description'] = '💀 **대실패!** 위대한 그분께서 당신의 시도를 거부하셨습니다...'
            return result
        
        if dice_sides >= 20:
            if total >= 20:
                result['success_level'] = 'critical_success'
                result['description'] = '🌟 **대성공!** 위대한 그분께서 당신을 축복하셨습니다!'
                return result
        
        if all(roll == dice_sides for roll in roll_list) and len(roll_list) > 0:
            result['success_level'] = 'critical_success'
            result['description'] = '✨ **완벽한 대성공!** 신비로운 운명의 손길입니다!'
            return result
        
        average = dice_sides / 2
        success_count = sum(1 for roll in roll_list if roll > average)
        
        if success_count >= len(roll_list) / 2:
            result['success_level'] = 'success'
            result['description'] = f'👁️ **성공!** {total}점의 신비로운 결과입니다...'
        else:
            result['success_level'] = 'failure'
            result['description'] = f'🌑 **실패.** {total}점... 우주는 당신의 노력을 거부합니다.'
        
        return result
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """메시지에서 [NdN] 패턴 감지하여 자동 롤"""
        if message.author == self.bot.user:
            return
        
        # ✅ 개선 #1: 빠른 필터링 추가 (성능 개선)
        if '[' not in message.content:
            return  # 정규표현식 검사 스킵!
        
        pattern = r'\[(\d+d\d+[\+\-]?\d*)\]'
        matches = re.findall(pattern, message.content)
        
        if not matches:
            return
        
        for notation in matches:
            await self._process_dice_roll(message, notation)
    
    async def _process_dice_roll(self, message: discord.Message, notation: str):
        """주사위 롤 처리 및 결과 표시"""
        try:
            dice_info = self.parse_dice_notation(notation)
            if not dice_info:
                await message.reply('❌ 올바른 주사위 표기법이 아닙니다. 예: `[2d6]` `[1d20+5]`')
                return
            
            async with message.channel.typing():
                loading_msg = await message.reply(f'🎲 위대한 그분께서 주사위를 대신 굴려주시는 중입니다...')
                # ✅ 개선 #2: asyncio.sleep 제거 (응답 시간 단축)
                
                rolls = self.roll_dice(dice_info['num_dice'], dice_info['dice_sides'])
                total = sum(rolls) + dice_info['modifier']
                
                success_info = self.determine_cthulhu_success(
                    total,
                    rolls,
                    dice_info['dice_sides']
                )
                
                dynamic_message = await self.perplexity.generate_dynamic_message({
                    'total': total,
                    'rolls': rolls,
                    'notation': notation,
                    'success_level': success_info['success_level']
                })
                
                embed = discord.Embed(
                    title=f'🎭 {message.author.name}의 주사위 굴림',
                    color=self._get_color_by_success(success_info['success_level'])
                )
                
                rolls_str = ', '.join([f'**{r}**' for r in rolls])
                embed.add_field(
                    name='🎲 주사위 결과',
                    value=f'{rolls_str}',
                    inline=False
                )
                
                if dice_info['modifier'] != 0:
                    modifier_str = f"+ {dice_info['modifier']}" if dice_info['modifier'] > 0 else f"- {abs(dice_info['modifier'])}"
                    embed.add_field(
                        name='➕ 계산',
                        value=f"`{sum(rolls)} {modifier_str} = **{total}**`",
                        inline=False
                    )
                else:
                    embed.add_field(
                        name='📊 주사위 합계',
                        value=f'**{total}**',
                        inline=False
                    )
                
                embed.add_field(
                    name='⚡ 판정',
                    value=success_info['description'],
                    inline=False
                )
                
                embed.add_field(
                    name='🌟 운명의 목소리',
                    value=f'*"{dynamic_message}"*',
                    inline=False
                )
                
                if dice_info['dice_sides'] == 100 or dice_info['dice_sides'] == 20:
                    embed.add_field(
                        name='📖 크툴루의 부름 규칙',
                        value=self._get_cthulhu_info(success_info['success_level'], total),
                        inline=False
                    )
                
                embed.set_footer(
                    text='🕷️ 위대한 그분께서 당신의 운명을 굴려주셨습니다.',
                    icon_url=message.author.avatar.url if message.author.avatar else None
                )
                
                await loading_msg.edit(content='⚡ 결과:', embed=embed)
        
        except Exception as e:
            logger.error(f'다이스 롤 오류: {e}')
            await message.reply(f'❌ 오류 발생: {str(e)}')
    
    def _get_color_by_success(self, success_level: str) -> discord.Color:
        """성공 레벨에 따른 색상"""
        colors = {
            'critical_success': discord.Color.gold(),
            'success': discord.Color.blue(),
            'failure': discord.Color.red(),
            'critical_failure': discord.Color.darker_gray()
        }
        return colors.get(success_level, discord.Color.purple())
    
    def _get_cthulhu_info(self, success_level: str, total: int) -> str:
        """크툴루 규칙 정보"""
        info = {
            'critical_success': '🌟 **완벽한 성공** - 이상의 기적이 일어났습니다!',
            'success': f'👁️ **성공** - {total}점으로 당신의 목표를 달성했습니다.',
            'failure': f'🌑 **실패** - {total}점... 목표 달성에 미쳤습니다.',
            'critical_failure': '💀 **대실패** - 끔찍한 결과입니다! 이제 무슨 일이...'
        }
        return info.get(success_level, '')

async def setup(bot):
    """Cog 로드"""
    await bot.add_cog(DiceRoller(bot))
    logger.info('✓ DiceRoller cog loaded')
