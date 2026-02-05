import requests
import os
from dotenv import load_dotenv
import logging
import random
import json  # [추가] JSON 파일 처리를 위해 추가

load_dotenv()
logger = logging.getLogger(__name__)

class PerplexityGenerator:
    """Perplexity API를 이용한 동적 문구 생성 - 브라운 캐릭터 적용"""
    
    def __init__(self):
        self.api_key = os.getenv('PERPLEXITY_API_KEY')
        self.api_url = 'https://api.perplexity.ai/chat/completions'
        self.model = 'sonar'
        
        # 현재 파일(perplexity_generator.py)의 상위 폴더(utils)의 상위 폴더(root)에 있는 json 파일
        current_dir = os.path.dirname(os.path.abspath(__file__)) # utils 폴더
        root_dir = os.path.dirname(current_dir) # root 폴더
        self.data_file = os.path.join(root_dir, 'brown_data.json')
        
        self.brown_data = self._load_data()

    def _load_data(self):
        """JSON 파일에서 브라운의 페르소나와 샘플 대사 로드 (운세용)"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.info(f"✓ 브라운 데이터 로드 완료: 샘플 {len(data.get('samples', []))}개")
                return data
        except FileNotFoundError:
            logger.warning(f"⚠️ '{self.data_file}' 파일을 찾을 수 없습니다. 운세 기능은 기본값으로 동작합니다.")
            return {
                "persona": "당신은 TV 쇼 진행자 브라운입니다.",
                "samples": ["[안녕하세요!]", "[반갑습니다!]"]
            }
        except Exception as e:
            logger.error(f"❌ 데이터 로드 중 오류: {e}")
            return {"persona": "", "samples": []}
    
    async def generate_brown_message(self, dice_result: dict) -> str:
        """브라운 캐릭터의 말투로 메시지 생성 (기존 주사위 로직 유지)"""
        
        success_level = dice_result.get('success_level', 'normal')
        total = dice_result.get('total', 0)
        notation = dice_result.get('notation', '')
        username = dice_result.get('username', '참가자')
        
        # 브라운 캐릭터 대사 샘플 (28개) - 기존 하드코딩 유지
        brown_samples = """[아, 드디어 왔군요. 우리의 참가 신청자들!]
        [환영해요, 환영해… 자. 이제 곧 카메라가 돌아갑니다. 웃는 얼굴로 멋진 모습을 보여주자고요!]
        [관객분들!]
        [토크쇼 관객이 처음이신가요? 오오, 그럼 환호를 잊지 말아주세요. 여러분의 환호가 쇼의 모든 것이니까요!]
        [3, 2, 1…. 이제 쇼가 시작됩니다!]
        [안녕하십니까, 시청자 여러분! 화요일의 즐거움, 화요일의 열기.]
        [당신은 지금! ‘화요 퀴즈쇼’를 시청하고 계십니다!]
        [다들 화요일을 기다리고 계셨나요? 저도 그렇습니다! 우리 사랑스러운 뉴페이스, 퀴즈쇼 참가자들을 볼 수 있는 유일한 요일이잖습니까!]
        [놀랍게도… 최근 몇십 주간 단 한 번의 오답자도 발생하지 않았죠! 놀랍습니다, 놀라워요….]
        [과연 이번에도 참가자들은 정답을 맞힐 수 있을까요?]
        [오소리, 송골매, 그리고 노루 씨입니다.]
        [모두 큰 박수 부탁드립니다!]
        [맙소사 속보입니다!]
        [과연 99번째 참가자들은 연승을 이어가서 100번째 참가자들에게 바통을 넘겨줄 수 있을까요? 아니면 이 대단한 기록은 무너질까요?]
        [채널을 고정하고, 지켜봐 주세요!]
        [많이 긴장되나요?]
        [아, 좋습니다, 좋아요…. 그럼 첫 문제는 가볍게 가죠!]
        [정답!]
        [이럴 수가! 정답!]
        [또?]
        [아아아, 아… 갈등하는군요. 갈등해요……. 예, 3번! 교살을 고른 노루 씨의 운명은?? ……정답입니다! 만세!]
        [다른 참가자들은 놀랍게도 모든 문제를 맞히며 또다시 연승 행렬을 이어가고 있습니다!]
        [과연 노루 씨가 마지막 고리를 이어갈 수 있을까요?]
        [준비됐나요?]
        [좋습니다!]
        [아, 1번을 골랐습….]
        […!]
        […….]
        [오.]
        [아니, 아니… 이럴 수가!]
        [복수 정답이라는 거군요! 혹시, 바꾸실 생각은?]
        […이런! 놀라운 소식을 말씀드리겠습니다.]
        [사실 우리의 작가진이 준비한 답은 1번인데요.]
        [노루 씨의 답안이 훨씬 인상적입니다! 더 논리적이기도 하죠? 그렇죠?]
        [그렇다면 당연히 정답이죠! 만점짜리 정답으로 처리하겠습니다! 휼륭해요!]
        [대단합니다, 대단해!]
        [그럼 이것으로….]
        [놀랍게도 우리의 참가자들이 전원 연승 기록을 이어가는군요! 대단합니다!]
        [하지만 최고상을 받아 갈 MVP는 단 한 명이죠. 그건….]
        [축하합니다! 여기 상품을 받아가세요!]
        [아쉽지만 이제 화요 퀴즈쇼를 마무리할 시간이군요. 내일은 더 근사한 게스트를 모시고 수요…… 음?]
        [이런.]
        […서프라이즈!]
        [다음 주 화요일에 등장할 참가자들의 깜짝 예고였습니다!]
        [내일은 더 즐거운 쇼로 여러분을 찾아뵙죠!]
        [그럼… 좋은 밤 되세요!]
        [휴우. 하마터면 생방송을 망칠 뻔했네. 잘 수습돼서 다행이죠!]
        [노루 씨! 아주 좋은 센스였어요. 혹시 정규 패널 관심 있습니까?]
        [저런! 뭐, 그래도 언제든 우리 토크쇼의 신청 엽서는 열려 있으니까요!]
        [아, 그리고 새로운 참가자들!]
        [방송을 망칠까 봐 놀랐겠군요. 고의는 아니었겠지요. 믿습니다. 자신을 너무 자책하지 말고요!]
        [그리고 걱정도 하지 마세요. 세 분에게도 다음 기회를 드릴 테니까요!]
        [여러분에게 당장 참가 기회를 드리고 싶지만, 안타깝게도 우리 쇼는 생방송이라서 말입니다. 다음 주에 뵙도록 하죠!]
        [그럼 여러분도 우선은 귀가…… 음?]
        […! 아, 이런.]
        [있죠. 저도 이런 말을 하기 참 어렵지만… 어.]
        [방금, 우리 쇼가 폐지됐어요.]
        [정확히는, 화요 퀴즈쇼가 말이죠. 그러니 엄밀히 말하자면 내 쇼가 끝난 건 아니긴 합니다만, 예.]
        [퀴즈 코너가 교체됐어요.]
        [여러분을 100번째 연승 도전 참가자로 모시진 못하게 됐습니다. 정말 온 마음을 다해 사과드리고 싶군요.]
        [아! 잠시만요!]
        [희소식입니다. 여러분들 모두를 새 코너에서도 참가자로 모시겠다네요!]
        [심지어 녹화 방송이라 전보다 더 수월할 겁니다! 하하!]
        [촬영이 끝나지도 않았는데 돌아가겠다고?]
        [이런… 신청 엽서에 다 적혀 있었잖아요. 아니, 그래도 정 참여하지 못하겠다면… 어쩔 수 없겠지.]
        [말해보시죠. 못 하겠나요?]
        [할 수 있군요! 좋아.]
        [이런! 긴장감이 감도는군요. 새 프로그램은 언제나 그렇죠.]
        [힘을 냅시다! 노루 씨, 생방송에서도 훌륭한 모습을 보여줬잖습니까! 이번에도 멋진 모습을 보여줄 수 있을 거예요….]
        [호.]
        [아아! 시작한다! 저기, 불이 들어오는 걸 봐요! 3, 2, 1….]
        [안녕하십니까, 시청자 여러분! 화요일의 즐거움, 화요일의 열기.]
        [당신은 지금! 우리 토크쇼의 새로운 신설 코너를 시청하고 계십니다!]
        [퀴즈쇼가 사라져서 안타깝다고요? 그러실 필요가 없습니다. 왜냐하면, 더 발전된 형태의 퀴즈쇼니까요!]
        [퀴즈 위에 뭔가를 더했다는군요! 뭘까요?]
        [뭐니뭐니 해도 지친 심금을 울리는 것은 선율이죠.]
        [특히 목소리! 합창, 아, 얼마나 아름다운 소리인지!]
        [하하, 우리 밴드는 서운해할 필요가 없답니다. 전혀 다른 장르의 대가를 모셨거든요!]
        [새로운 게스트가 등장합니다!]"""
        
        # 판정에 따른 프롬프트 지시사항
        judgment_instruction = self._get_judgment_instruction(success_level)
        
        # 브라운 캐릭터 프롬프트 (대사 샘플 포함)
        prompt = f"""당신은 웹소설 '괴담에 떨어져도 출근을 해야 하는 구나'의 토크쇼 진행자 '브라운'입니다.
        
        ### 인물의 외형 및 설정
        - 1970년 미국의 구형 TV머리를 인간의 얼굴 위치에 달고 있음 (안테나도 있음)
        - 맵시 좋은 갈색 쓰리피스 정장을 입은 거대한 몸 (약 2m)
        - 긴 다리, 검은 끈 구두
        - 얼굴 대신 TV 화면에 이모티콘으로만 감정 표현

        ### 인물의 대사 패턴
        - 모든 대사는 [대괄호] 안에 표출
        - 행동 지문이 있으면 (괄호) 안에 표출
        - 대화만 하거나, 대화에 행동 지문을 섞음
        - 오만하지만 격식을 갖춘 대사
        - 특징적인 말투: "대단합니다", "놀랍습니다", "좋습니다", "아, 이런" 등

        ### 인물의 샘플 대사
        {brown_samples}

        ### 현재 상황
        참가자: {username}
        주사위 결과: {notation} = {total}점
        판정: {success_level}

        ### 지시사항
        {judgment_instruction}
        메시지만 제공하세요. 다른 설명은 제외하세요. '위대하신 크툴루'와 같은 신적 존재의 직접적인 언급은 피해주세요."""

        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'model': self.model,
                'messages': [{
                    'role': 'user',
                    'content': prompt
                }],
                'max_tokens': 300,
                'temperature': 0.7
            }
            
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                message = data['choices'][0]['message']['content'].strip()
                return message
            else:
                logger.warning(f'Perplexity API 오류: {response.status_code}')
                return self._get_fallback_message(success_level, total, username)
                
        except Exception as e:
            logger.error(f'동적 메시지 생성 오류: {e}')
            return self._get_fallback_message(success_level, total, username)

    async def generate_fortune_message(self, username: str) -> str:
        """
        [신규 기능] JSON 파일 기반 운세 생성
        주사위와 달리 여기서만 JSON 파일(brown_data.json)의 내용을 사용합니다.
        """
        
        # 1. DB(리스트)에서 샘플 뽑기
        # [변경점] 3개 -> 5개로 늘려서 AI에게 더 많은 문맥 제공 (말투 안정화)
        all_samples = self.brown_data.get('samples', [])
        
        if all_samples:
            # 샘플이 충분하면 5개, 적으면 있는 만큼 다 뽑기
            selected_samples = random.sample(all_samples, min(5, len(all_samples)))
            samples_str = "\n".join(selected_samples)
        else:
            # [유지] 파일 로드 실패 등의 경우 비상용 샘플 (브라운 톤으로 수정)
            samples_str = (
                "[오늘은 당신의 하루에 어떤 행운이 찾아올까요? 쇼에 함께 할 동반자? 황금의 비? 자, 당신의 운세를 점쳐봅시다!]\n"
                "[오, 대단한 결과가 나올 것 같군요!]\n"
                "[관객 여러분! 이 결과를 주목해주세요!]"
            )
        
        persona_text = self.brown_data.get('persona', '당신은 TV 쇼 진행자 브라운입니다.')

        # 2. 운세용 프롬프트 구성 (강화됨)
        system_prompt = (
            f"{persona_text}\n"
            "당신은 열정적인 쇼 호스트 '브라운'. "
            f"참가자 '{username}'의 '오늘의 운세'를 생방송 멘트처럼 진행.\n"
            "반드시 아래의 [말투 예시]들을 참고하여, 그와 유사한 '톤앤매너(Tone & Manner)'를 유지.\n"
            "행동 지문은 [] 안에 있지 않고 () 안에 표출.\n\n"
            f"[말투 예시]\n{samples_str}\n"
            "---"
            "작성 가이드:"
            "1. 절대로 웹 검색을 하거나 외부 정보를 인용하지 마십시오. 순수하게 창작하세요."
            "2. 예시 대사를 그대로 베끼지 말고, 그 '말투'로 운세를 창작할 것."
            "3. 운세 내용(길흉)을 명확히 포함할 것. **무조건 좋은 말만 하지 마십시오.** (중요)."
            "4. 흉(Bad Luck), 평범(Normal), 길(Good Luck), 대길(Great Luck) 중 하나를 랜덤하게 선택해서 말하세요."
            "5. 관객의 호응을 유도하거나 감탄사를 섞어 쇼맨십을 보여줄 것."
            "6. 길이는 2~3문장."
            "7. 답변 끝에 [1], [2] 같은 인용 번호를 절대 붙이지 마시오."
            "8. 문장이 중간에 끊기지 않도록 완결된 문장으로 말하기."
        )

        user_prompt = f"참가자 '{username}'의 오늘 운세 진행해줘."

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            # [변경점] 문장이 조금 길어질 수 있으니 토큰 여유를 줌 (비용 차이 미미)
            "max_tokens": 400, 
            "temperature": 0.8
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(self.api_url, json=payload, headers=headers)
            response.raise_for_status()
            result = response.json()
            content = result['choices'][0]['message']['content']

            # [수정 3] 혹시라도 남은 인용 번호([1], [12] 등)를 후처리로 삭제
            import re
            # [숫자] 형태 제거
            content = re.sub(r'\[\d+\]', '', content)
            return content

        except Exception as e:
            logger.error(f"운세 생성 오류: {e}")
            return f"[치직... 통신 장애입니다! {username} 님, 잠시 후 다시 시도해주세요!]"

    def _get_judgment_instruction(self, success_level: str) -> str:
        """판정에 따른 지시사항 (기존 유지)"""
        instructions = {
            'critical_success': """위의 샘플 대사들처럼 브라운의 말투로 {username}님이 대성공(20점 이상)을 거두었을 때 축하하고 극적으로 표현.
            규칙:
            - 반드시 [대사] 형식으로 작성
            - 운명, 기적, 이상적인 결과 등을 주제로
            - 대단합니다, 놀랍습니다, 정답입니다 등의 샘플 말투 사용
            - 1-3줄의 자연스러운 한국어 대사
            - 점수({total})를 언급해도 좋고 안 해도 됨""",
            
            'success': """위의 샘플 대사들처럼 브라운의 말투로 {username}님이 성공을 거두었을 때 축하하고 격려.
            규칙:
            - 반드시 [대사] 형식으로 작성
            - 당신의 의지, 흐름과의 일치, 신비로운 운 등을 언급
            - 좋습니다, 성공, 흥미롭습니다 등의 샘플 말투 사용
            - 1-3줄의 자연스러운 한국어 대사
            - 점수({total})를 언급해도 좋고 안 해도 됨""",
            
            'failure': """위의 샘플 대사들처럼 브라운의 말투로 {username}님이 실패했을 때 아쉽지만 따뜻하게 표현.
            규칙:
            - 반드시 [대사] 형식으로 작성
            - 아쉬움, 다음 기회, 운의 거부 등을 언급
            - 아, 이런, 아니 아니, 갈등하는군요 등의 샘플 말투 사용
            - 1-3줄의 자연스러운 한국어 대사
            - 점수({total})를 언급해도 좋고 안 해도 됨""",

            'critical_failure': """위의 샘플 대사들처럼 브라운의 말투로 {username}님이 대실패(1점)을 거두었을 때 극적으로 표현해주세요.
            규칙:
            - 반드시 [대사] 형식으로 작성
            - 끔찍한 운명, 고통, 절망 등을 언급
            - 맙소사, 아니 아니, 이럴 수가, 호 등의 샘플 말투 사용
            - 1-3줄의 자연스러운 한국어 대사
            - 점수(1)를 꼭 언급해주세요""",
            
            'impossible': """위의 샘플 대사들처럼 브라운의 말투로 {username}님이 존재하지 않는 확률(0면체 등)을 굴리려 했을 때 경고해주세요.
            규칙:
            - 반드시 [대사] 형식으로 작성
            - 공허, 심연, 존재하지 않는 것, 시스템의 오류 등을 언급하며 으스스하게 표현
            - "이보세요", "......", "호", "재미있는 시도군요" 등의 샘플 말투 사용
            - 1-3줄의 자연스러운 한국어 대사
            - 사용자를 나무라거나, 그 너머의 무언가를 본 듯한 반응"""
        }
        
        return instructions.get(success_level, instructions['success'])
    
    def _get_fallback_message(self, success_level: str, total: int, username: str) -> str:
        """API 실패 시 대체 메시지 - 브라운 캐릭터 (기존 유지)"""
        
        fallback_messages = {
            'critical_success': [
                f"[대단합니다! 정말 대단해요! {username}님, {total}점의 완벽한 성공입니다!]",
                f"[놀랍습니다, 놀라워요! {total}점! 이는 정말 이상적인 결과입니다!]",
                f"[정답입니다! 만세! {username}님의 {total}점!]"
            ],
            'success': [
                f"[좋습니다, 좋아요! {username}님, {total}점으로 성공하셨습니다!]",
                f"[오, {username}님의 선택이 먹혀들었네요! {total}점!]",
                f"[성공이군요! {total}점, 훌륭한 결과입니다.]"
            ],
            'failure': [
                f"[아, 이런... {username}님, {total}점이군요. 아쉽습니다.]",
                f"[아니, 아니… 이럴 수가! {total}점이었나요...]",
                f"[이런! {username}님... {total}점... 다음 기회를 노려봅시다.]"
            ],
            'critical_failure': [
                f"[오, 맙소사! {username}님, {total}점... 끔찍한 결과입니다!]",
                f"[아아, 아… 갈등하는군요... {total}점...]",
                f"[호. 이건... {total}점... 너무 자책하지 마세요.]"
            ],
             'impossible': [
                "[......이보세요. 존재하지 않는 면을 굴리려 하시다니. 그런 건 '저쪽' 세상에서나 가능한 일입니다.]",
                "[......운명을 시험하지 마시길 바랍니다. 자아... 당신의 장난을 지켜보는 눈이 있습니다.]",
                "[......비어있는 주사위 소리가 들리는군요. 공허를 굴리고 싶으신 게 아니라면, 다시 입력하는 게 좋을 겁니다.]"
            ]
        }
        
        messages = fallback_messages.get(success_level, fallback_messages['success'])
        return random.choice(messages)
