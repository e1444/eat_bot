import llm
import re

from constants import *

model = llm.get_model("gpt-3.5-turbo")
model.key = OPENAI_API_KEY

def random_encounter_script(noun: str) -> list[str]:
    response = model.prompt(PROMPT(noun), SYSTEM_PROMPT)

    script = response.text()
    script = script.split('\n')
    script = [line for line in script if line]
    script = [line for line in script if ':' in line]
    script = [line.split(':') for line in script]
    script = [(line[0].strip(), line[1].strip()) for line in script]
    script = [(line[0], re.sub(r'@p1', 'eat_bot', line[1])) for line in script]
    script = [(line[0], re.sub(r'@p2', noun, line[1])) for line in script]
    
    return script

from openai import OpenAI

salad_messages = [
    {
        "role": "user",
        "content": "Knowledge: \"Word salad: a jumble of extremely incoherent speech as sometimes observed in schizophrenia\"\n# Turn the following text into a word salad. Only use words in the prompt."
    },
    {
        "role": "user",
        "content": "text: <I might have to explain to my dogs why i can't stop laughing>\nSalad:"
    },
    {
        "role": "assistant",
        "content": "I dogs laughing explain might stop have can't my to why to have to I my dogs I stop to laughing."
    },
    {
        "role": "user",
        "content": "text: <Can u sex while pregat, dangerops will hurt baby top of his head!?!>\nSalad:"
    },
    {
        "role": "assistant",
        "content": "pregat head top baby sex hurt dangerops can while!?!"
    }
    ]

def saladify(text: str) -> str:
    text = 'Text: <' + text + '>\nSalad:'
    prompt = {'role': 'user', 'content': text}
    
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=salad_messages + [prompt],
        temperature=1,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    return response.choices[0].message.content 