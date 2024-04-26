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

def saladify(text: str) -> str:
    text = """Turn the following prompt into a word salad. Only use words in the prompt.
""" + text
    response = model.prompt(text)
    
    return response.text()