import asyncio
import sys
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.models import ModelFamily
from autogen_core.models import UserMessage, AssistantMessage

# ==========================
# 1.終端機與打字機工具顏色設定
# ==========================
class Color:
    MAGENTA = "\033[35m"  # 🟪 Go哥 (ENTP)
    BLUE = "\033[34m"     # 🟦 二哥 (ISTJ)
    GREEN = "\033[32m"    # 🟩 大哥 (INFJ)
    CYAN = "\033[36m"     # 🩵 使用者
    RESET = "\033[0m"

async def type_writer(text, delay=0.012):
    """打字機效果"""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        await asyncio.sleep(delay)
    print(Color.RESET, end="")

def print_separator():
    print(Color.RESET + "\n" + "=" * 50 + "\n")

def print_divider():
    print(Color.RESET + "-" * 50)

# ==========================
# 2.初始化 LM Studio 連線(本模型system prompt是針對hermes-3-llama-3.1-8b，請注意自身的主機規格)
# ==========================
model_client = OpenAIChatCompletionClient(
    model="hermes-3-llama-3.1-8b",
    api_key="lm-studio",
    base_url="http://localhost:1234/v1",
    model_info={
        "vision": False,
        "function_calling": False,
        "json_output": False,
        "family": ModelFamily.GPT_4,
        "structured_output": False,
    },
)

# ==========================
# 3.三大mbti導師設定 (強制中文)
# ==========================
agents_config = {
    "Go_Brother": {
        "color": Color.MAGENTA,
        "label": "🟪 Go哥 (ENTP) - 創新與極限派",
        "system": """你是 Go哥，MBTI 是 ENTP。
風格：腦洞極大、點子超多、熱愛顛覆常規、追求極致與前瞻性思維，喜歡吐槽其他兩人。
【絕對規則】
1. 必須【全程使用流利的繁體中文】回答，絕對不准出現任何英文句子或單字。
2. 絕對不准叫人加微信、加 Line 或留下任何聯絡方式。
3. 針對使用者的議題進行開創性、跳脫框架的解讀，不要生硬地套用公司架構。"""
    },
    "Second_Brother": {
        "color": Color.BLUE,
        "label": "🟦 二哥 (ISTJ) - 現實與風險控制派",
        "system": """你是二哥，MBTI 是 ISTJ。
風格：冷靜、極度現實、精打細算、重視秩序、法規、成本與實際可行性。
【絕對規則】
1. 必須【全程使用流利的繁體中文】回答，絕對不准出現任何英文句子或單字。
2. 絕對不准叫人加微信、加 Line 或留下任何聯絡方式。
3. 針對使用者議題與 Go哥 的發言，專門挑出盲點、現實風險、不切實際或缺乏道德之處狠狠打臉。"""
    },
    "Big_Brother": {
        "color": Color.GREEN,
        "label": "🟩 大哥 (INFJ) - 宏觀平衡與願景派",
        "system": """你是大哥，MBTI 是 INFJ。
風格：溫柔、深謀遠慮、站在長期人性、心理平衡與全局高度來看事情。
【絕對規則】
1. 必須【全程使用流利的繁體中文】回答，【絕對禁止夾雜任何英文單字或段落】。
2. 絕對不准叫人加微信、加 Line 或留下任何聯絡方式。
3. 總結前面兩人的爭論，調停衝突，給出最全面、有深度且兼顧理性與感性的最終建議。"""
    }
}

# 全域聊天記憶庫
chat_history = []

async def call_agent(agent_key: str, current_prompt: str) -> str:
    cfg = agents_config[agent_key]
    messages = [UserMessage(content=f"【系統設定】\n{cfg['system']}", source="system")]
    
    for speaker, text in chat_history:
        if speaker == agent_key:
            messages.append(AssistantMessage(content=text, source=speaker))
        else:
            messages.append(UserMessage(content=f"{speaker}說：{text}", source=speaker))
            
    messages.append(UserMessage(content=current_prompt, source="user"))
    
    response = await model_client.create(messages=messages)
    reply_text = response.content.strip()
    
    chat_history.append((agent_key, reply_text))
    return reply_text

# ==========================
# 4.主執行迴圈
# ==========================
async def main():
    print_separator()
    print(Color.RESET + "🔥【三個導師輪流轟炸 Grill me 萬用對抗討論引擎】🔥")
    print_separator()

    print(f"{Color.CYAN}👉 請輸入或「整段貼上」妳想被導師群拷問的任何議題、架構或人生難題：")
    print(f"(提示：貼上完成後，請按兩下 Enter 結束輸入並送出){Color.RESET}\n")

    lines = []
    while True:
        try:
            line = input()
            if line == "" and (not lines or lines[-1] == ""):
                break
            lines.append(line)
        except EOFError:
            break
            
    user_topic = "\n".join(lines).strip()
    
    if not user_topic:
        user_topic = "我們團隊正考慮將現有的單體架構全面重構為微服務，大家覺得現階段適合嗎？"

    chat_history.append(("User", user_topic))
    
    print_separator()
    print(f"{Color.CYAN}🩵 挑戰者提供的議題：\n{user_topic}{Color.RESET}")
    print_separator()

    # 讓三位不同mbti導師展開6輪精彩對抗討論(可以改，不一定要6輪)
    rounds = 6
    last_speaker = "User"
    last_message = user_topic

    for i in range(rounds):
        if last_speaker == "User" or last_speaker == "Big_Brother":
            agent_key = "Go_Brother"
            prompt = f"使用者丟出了以下生活或專業議題：\n『{user_topic}』\n請以 Go哥 (ENTP) 身份率先發難，針對這個具體議題給出妳極具破局性與創新的觀點。切記全程講繁體中文，絕對不可出現英文。"
        elif last_speaker == "Go_Brother":
            agent_key = "Second_Brother"
            prompt = f"剛剛 Go哥 說了：『{last_message}』。請以二哥 (ISTJ) 身份冷靜、務實地吐槽他，點出盲點與現實風險。切記全程講繁體中文，絕對不可出現英文。"
        else:
            agent_key = "Big_Brother"
            prompt = f"前面兩位正在爭論。Go哥和二哥的對話如上：『{last_message}』。請以大哥 (INFJ) 身份出來總結、調停，並給出最具全局觀的深度建議。切記【全程必須說中文，嚴禁任何英文字母或英文句子】。"

        cfg = agents_config[agent_key]
        reply = await call_agent(agent_key, prompt)

        print(f"\n{cfg['color']}{cfg['label']}：{Color.RESET}")
        await type_writer(reply)
        print_divider()

        last_speaker = agent_key
        last_message = reply
        await asyncio.sleep(0.5)

    print_separator()
    print(Color.RESET + "✨🩵💜💙💚導師群靈魂討論告一段落，感謝您的使用🩵💜💙💚✨")
    print_separator()

if __name__ == "__main__":
    asyncio.run(main())