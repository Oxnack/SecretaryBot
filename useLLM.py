from config import *
import openai  # For DeepSeek req


client = openai.OpenAI(
    api_key=API_KEY,
    base_url="https://api.deepseek.com"
)


def process(prompt):
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": PRED_PROMPT},
            {"role": "user", "content": prompt}
        ]
    )
    print("proc done")
    return response.choices[0].message.content