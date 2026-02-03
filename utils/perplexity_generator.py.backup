import requests
import os
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)

class PerplexityGenerator:
    """Perplexity API를 이용한 동적 문구 생성"""
    
    def __init__(self):
        self.api_key = os.getenv('PERPLEXITY_API_KEY')
        self.api_url = 'https://api.perplexity.ai/chat/completions'
        self.model = 'sonar'
    
    async def generate_dynamic_message(self, dice_result: dict) -> str:
        """주사위 결과를 받아 동적 문구 생성"""
        try:
            success_level = dice_result.get('success_level', 'normal')
            total = dice_result.get('total', 0)
            notation = dice_result.get('notation', '')
            
            # 프롬프트 엔지니어링
            prompts = {
                'critical_success': f"""당신은 크툴루의 부름 RPG의 나레이터입니다.
주사위 결과가 대성공(Critical Success)했습니다: {total}점 (주사위: {notation})
이 대성공을 축하하는 짧고 재미있는 한국어 1-2줄 메시지를 만들어주세요. 
초자연적이고 신비로운 톤으로, 마치 위대한 그분(Cthulhu)이 축복을 내려주는 느낌으로 작성해주세요.
메시지만 작성하고 설명은 제외하세요.""",
                
                'success': f"""당신은 크툴루의 부름 RPG의 나레이터입니다.
주사위 결과가 성공(Success)했습니다: {total}점 (주사위: {notation})
이 성공을 축하하는 짧고 위트있는 한국어 1-2줄 메시지를 만들어주세요.
신비로운 톤으로, 마치 당신의 행운이 특별함을 암시하는 느낌으로 작성해주세요.
메시지만 작성하고 설명은 제외하세요.""",
                
                'failure': f"""당신은 크툴루의 부름 RPG의 나레이터입니다.
주사위 결과가 실패(Failure)했습니다: {total}점 (주사위: {notation})
이 실패를 동정적이면서도 유머있게 표현하는 짧은 한국어 1-2줄 메시지를 만들어주세요.
마치 우주의 위대한 힘이 당신의 노력을 무시하는 느낌으로 작성해주세요.
메시지만 작성하고 설명은 제외하세요.""",
                
                'critical_failure': f"""당신은 크툴루의 부름 RPG의 나레이터입니다.
주사위 결과가 대실패(Critical Failure)했습니다: {total}점 (주사위: {notation})
이 끔찍한 대실패를 극적이고 재미있게 표현하는 짧은 한국어 1-2줄 메시지를 만들어주세요.
마치 위대한 그분께서 당신의 시도를 조롱하는 느낌으로, 검은 유머를 섞어서 작성해주세요.
메시지만 작성하고 설명은 제외하세요."""
            }
            
            prompt = prompts.get(success_level, prompts['success'])
            
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'model': self.model,
                'messages': [
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                'max_tokens': 150,
                'temperature': 0.6  # ✅ 개선 #3: 0.8 → 0.6 (일관성 개선)
            }
            
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                message = data['choices']['message']['content'].strip()
                return message
            else:
                logger.warning(f'Perplexity API 오류: {response.status_code}')
                return self._get_fallback_message(success_level, total)
        
        except Exception as e:
            logger.error(f'동적 메시지 생성 오류: {e}')
            return self._get_fallback_message(success_level, total)
    
    def _get_fallback_message(self, success_level: str, total: int) -> str:
        """API 실패 시 대체 메시지"""
        fallback_messages = {
            'critical_success': [
                f'🌟 당신의 행운은 무한합니다! {total}점의 기적이 일어났습니다!',
                f'✨ 위대한 그분께서 축복을 내려주셨습니다! {total}점!',
                f'🎭 이것이 진정한 대성공의 운명입니다! {total}점!',
            ],
            'success': [
                f'👁️ 당신의 시도는 성공했습니다. {total}점.',
                f'🔮 신비로운 힘이 당신을 도왔습니다. {total}점.',
                f'⚡ 당신의 결정이 먹혀들었습니다. {total}점.',
            ],
            'failure': [
                f'🌑 하늘은 당신의 바람을 들으셨지만... {total}점.',
                f'💀 우주는 당신의 노력을 거부합니다. {total}점.',
                f'🕷️ 끔찍한 실패입니다. {total}점.',
            ],
            'critical_failure': [
                f'🌀 이것은... 재앙입니다! {total}점!',
                f'💥 최악의 결과입니다! {total}점!',
                f'🔥 당신의 행운은 완전히 소진되었습니다! {total}점!',
            ]
        }
        
        import random
        messages = fallback_messages.get(success_level, fallback_messages['success'])
        return random.choice(messages)
