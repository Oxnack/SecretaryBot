import openai  # DeepSeek использует совместимый с OpenAI API

client = openai.OpenAI(
    api_key="sk-2ca5b4ee6e46446a8d5fbf652cd262c7",
    base_url="https://api.deepseek.com"
)

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "user", "content": "Привет, друг, ответь на русском пожалуйста, а ещё скажи какая ты модель?"}
    ]
)
print(response.choices[0].message.content)