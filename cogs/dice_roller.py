import discord
from discord.ext import commands
import re
import random
import logging
# from utils.gemini_generator import GeminiGenerator
from utils.perplexity_generator import PerplexityGenerator

logger = logging.getLogger(__name__)

class DiceRoller(commands.Cog):
    """D&D & 크툴루의 부름 다이스 롤러 - 브라운 캐릭터 자동 적용"""

    def __init__(self, bot):
        self.bot = bot
        self.perplexity = PerplexityGenerator()
        self.cthulhu_difficulties = {
            'regular': 1.0,
            'hard': 0.5,
            'extreme': 0.2,
        }

    def parse_dice_notation(self, notation: str) -> dict | None:
        """다이스 표기법 파싱 (에러 타입 세분화)"""
        notation = notation.strip('[]')
        pattern = r'^(\d+)d(\d+)([\+\-]\d+)?$'
        match = re.match(pattern, notation)

        if not match:
            return None

        num_dice = int(match.group(1))
        dice_sides = int(match.group(2))
        modifier = int(match.group(3)) if match.group(3) else 0

        # 1. 불가능한 주사위 (0)
        if num_dice == 0 or dice_sides == 0:
            return {'error': 'impossible', 'notation': notation}

        # 2. 주사위 개수 초과 (예: 100개 초과)
        if num_dice > 100:
            return {'error': 'too_many_dice', 'limit': 100}

        # 3. 주사위 면체 초과 (예: 1000면 초과)
        if dice_sides > 1000:
            return {'error': 'too_large_sides', 'limit': 1000}

        # 4. 정상
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
            result['description'] = '💀 대실패'
            return result

        if dice_sides >= 20:
            if total >= 20:
                result['success_level'] = 'critical_success'
                result['description'] = '🌟 대성공'
                return result

        if all(roll == dice_sides for roll in roll_list) and len(roll_list) > 0:
            result['success_level'] = 'critical_success'
            result['description'] = '🌟 대성공'
            return result

        average = dice_sides / 2
        success_count = sum(1 for roll in roll_list if roll > average)

        if success_count >= len(roll_list) / 2:
            result['success_level'] = 'success'
            result['description'] = '👁️ 성공'
        else:
            result['success_level'] = 'failure'
            result['description'] = '🌑 실패'

        return result

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """메시지에서 [NdN] 패턴 감지하여 자동 롤"""
        if message.author == self.bot.user:
            return

        if '[' not in message.content:
            return

        pattern = r'\[(\d+d\d+[\+\-]?\d*)\]'
        matches = re.findall(pattern, message.content)

        if not matches:
            return

        for notation in matches:
            await self._process_dice_roll(message, notation)

    async def _process_dice_roll(self, message: discord.Message, notation: str):
        """주사위 롤 처리 및 에러 대응"""
        try:
            dice_info = self.parse_dice_notation(notation)

            # 1. 파싱 자체가 안 된 경우 (정규식 불일치) -> 무시
            if not dice_info:
                return

            # 2. 에러 케이스 처리
            if 'error' in dice_info:
                error_type = dice_info['error']
                response_msg = ""

                # Case A: 불가능한 수치 (0) - API 사용
                if error_type == 'impossible':
                    async with message.channel.typing():
                        dummy_result = {
                            'success_level': 'impossible', 'total': 0,
                            'notation': notation, 'username': message.author.display_name
                        }
                        response_msg = await self.perplexity.generate_brown_message(dummy_result)
                        await message.reply(f"👻 {response_msg}")
                    return

                # Case B: 주사위 개수가 너무 많음
                elif error_type == 'too_many_dice':
                    quotes = [
                        "[이런, 욕심이 과하시군요. 주사위는 100개까지만 허용됩니다. 그 이상은 스튜디오 바닥이 어지러워지거든요.]",
                        "[잠시만요. 그렇게 많은 주사위를 한꺼번에 던지면 방송 사고가 납니다. 적당히 나눠서 굴리시죠?]",
                        "[호. 손은 두 개뿐인데 주사위를 그렇게 많이 쥐시려고요? 100개 이하로 줄여주세요.]"
                    ]
                    response_msg = random.choice(quotes)

                # Case C: 주사위 면체가 너무 큼
                elif error_type == 'too_large_sides':
                    quotes = [
                        "[호. 1000면이 넘는 주사위라니? 그런 건 거의 구에 가깝죠. 굴러가다 영원히 멈추지 않을 겁니다.]",
                        "[참가자분, 우리 스튜디오엔 그런 거대한 주사위가 없습니다. 1000면 이하의 상식적인 주사위를 사용해주세요.]",
                        "[저런. 숫자가 너무 크군요. 그 정도 확률은 신의 영역에 맡겨두는 게 좋겠습니다.]"
                    ]
                    response_msg = random.choice(quotes)

                # 에러 메시지 전송
                await message.reply(response_msg)
                return

            # 3. 정상 처리
            await self._roll_and_display(message, notation, dice_info)

        except Exception as e:
            logger.error(f'다이스 롤 오류: {e}')
            await message.reply(f'❌ [시스템 오류] 방송 장비에 문제가 생겼군요: {str(e)}')

    # async def _roll_and_display(self, message: discord.Message, notation: str, dice_info: dict):
    #     """주사위를 굴리고 결과 표시"""
    #     async with message.channel.typing():
    #         loading_msg = await message.reply(f'🎲 위대하고 전지전능하신 그분께서 주사위를 대신 굴려주시는 중입니다...')

    #         rolls = self.roll_dice(dice_info['num_dice'], dice_info['dice_sides'])
    #         total = sum(rolls) + dice_info['modifier']

    #         success_info = self.determine_cthulhu_success(
    #             total,
    #             rolls,
    #             dice_info['dice_sides']
    #         )

    #         # Perplexity API에 판정 정보도 함께 전송
    #         dynamic_message = await self.perplexity.generate_brown_message({
    #             'total': total,
    #             'rolls': rolls,
    #             'notation': notation,
    #             'success_level': success_info['success_level'],
    #             'username': message.author.display_name
    #         })

    #         # 주사위 결과 포맷
    #         rolls_str = ', '.join([str(r) for r in rolls])

    #         # 계산 과정 포맷
    #         if dice_info['modifier'] != 0:
    #             modifier_str = f"+ {dice_info['modifier']}" if dice_info['modifier'] > 0 else f"- {abs(dice_info['modifier'])}"
    #             calculation = f"{sum(rolls)} {modifier_str} = **{total}**"
    #         else:
    #             calculation = f"**{total}**"

    #         # Embed 생성
    #         embed = discord.Embed(
    #             title=f'{message.author.display_name}님의 운명',
    #             color=self._get_color_by_success(success_info['success_level']),
    #             description='위대하신 그분 께서 주사위를 굴려주셨습니다.'
    #         )

    #         # 1단계: 주사위 결과
    #         embed.add_field(
    #             name='📍 주사위 결과',
    #             value=rolls_str,
    #             inline=False
    #         )

    #         # 2단계: 합계
    #         embed.add_field(
    #             name='📊 주사위 합계',
    #             value=calculation,
    #             inline=False
    #         )

    #         # 3단계: 판정
    #         embed.add_field(
    #             name='⚡ 판정',
    #             value=success_info['description'],
    #             inline=False
    #         )

    #         # 운명의 목소리
    #         embed.add_field(
    #             name='🎤 운명의 목소리가 들려오는군요...',
    #             value=dynamic_message,
    #             inline=False
    #         )

    #         embed.set_footer(
    #             text='🕷️ 위대하신 그분께서 당신의 운명을 굴려주셨습니다.',
    #             icon_url=message.author.avatar.url if message.author.avatar else None
    #         )

    #         await loading_msg.edit(content='', embed=embed)

    async def _roll_and_display(self, message: discord.Message, notation: str, dice_info: dict):
        """주사위를 굴리고 결과 표시 (Text 버전)"""
        async with message.channel.typing():
            # (로딩 메시지는 유지하거나 생략 가능)
            
            rolls = self.roll_dice(dice_info['num_dice'], dice_info['dice_sides'])
            total = sum(rolls) + dice_info['modifier']
            
            success_info = self.determine_cthulhu_success(
                total, rolls, dice_info['dice_sides']
            )
            
            # AI 메시지 생성
            dynamic_message = await self.perplexity.generate_brown_message({
                'total': total,
                'rolls': rolls,
                'notation': notation,
                'success_level': success_info['success_level'],
                'username': message.author.display_name
            })
            
            # 결과 텍스트 포맷팅
            rolls_str = ', '.join([str(r) for r in rolls])
            
            if dice_info['modifier'] != 0:
                modifier_str = f"+ {dice_info['modifier']}" if dice_info['modifier'] > 0 else f"- {abs(dice_info['modifier'])}"
                calculation = f"{sum(rolls)} {modifier_str} = **{total}**"
            else:
                calculation = f"{total}"

            # 성공/실패 이모지
            result_emoji = {
                'critical_success': '🌟 대성공!',
                'success': '👁️ 성공',
                'failure': '🌑 실패',
                'critical_failure': '💀 대실패...'
            }.get(success_info['success_level'], '결과')

            # [최종 메시지 조립]
            # 1. 브라운의 대사 (인용구 처리 >)
            # 2. 주사위 결과 요약
            final_text = (
                f"## 🎙️ {dynamic_message}\n"  # ##는 제목2 (적당히 큼)
                f"> **{message.author.display_name}**님의 굴림: `{notation}`\n"
                f"> ⚡ 결과: `[{rolls_str}]` → **{total}** ({result_emoji})"
            )
            
            # 메시지 전송 (reply로 답장)
            await message.reply(final_text)

    def _get_color_by_success(self, success_level: str) -> discord.Color:
        """성공 레벨에 따른 색상"""
        colors = {
            'critical_success': discord.Color.gold(),
            'success': discord.Color.blue(),
            'failure': discord.Color.red(),
            'critical_failure': discord.Color.darker_gray()
        }
        return colors.get(success_level, discord.Color.purple())

async def setup(bot):
    """Cog 로드"""
    await bot.add_cog(DiceRoller(bot))
    logger.info('✓ DiceRoller cog loaded')
