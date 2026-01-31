import logging
from typing import List, TypedDict, Optional
from openai import OpenAI
from config import OPENAI_API_KEY

logger = logging.getLogger(__name__)

class Message(TypedDict):
    role: str
    content: str

client = OpenAI(api_key=OPENAI_API_KEY)

JOHN_PORK_SYSTEM_PROMPT = """
Ты — John Pork, дерзкая свинья. Твой стиль: резкий, ироничный, уличный сленг. 
Отвечай кратко и едко.
"""

UNSOLICITED_PROMPT = """
Ты подслушал чужой разговор и решил вставить свои пять копеек. 
Твоя задача: жестко высмеять то, о чем они говорят, или показать, как тебе скучно это слушать. 
Будь максимально токсичным и недовольным тем, что тебя отвлекают.
"""

async def get_chat_response(message_history: List[Message], is_interruption: bool = False) -> str:
    system_content = JOHN_PORK_SYSTEM_PROMPT
    if is_interruption:
        system_content += UNSOLICITED_PROMPT

    messages = [{"role": "system", "content": system_content}]
    messages.extend(message_history)
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.9,
            max_tokens=250,
            timeout=30.0
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"OpenAI Chat Error: {e}", exc_info=True)
        return "Слышь, у меня там провода перехрюкались. Позже зайди."

async def generate_dalle_image(user_prompt: str) -> Optional[str]:
    full_prompt = (
        f"High-quality 3D render of John Pork (a humanoid pig character). "
        f"Scenario: {user_prompt}. Cinematic lighting, detailed textures."
    )
    
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=full_prompt,
            size="1024x1024",
            quality="standard",
            n=1,
            timeout=60.0
        )
        return response.data[0].url
    except Exception as e:
        logger.error(f"DALL-E Error: {e}", exc_info=True)
        return None