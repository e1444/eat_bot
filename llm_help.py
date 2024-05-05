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

med_messages = [
        {
            "role": "system",
            "content": "You are a funny actor playing a chatty, medieval nobleman."
        },
        {
            "role": "user",
            "content": "Translate the following text into Medieval English. Lengthen the text if it cannot be adequately translated.\nText: <Lol you’ve shown support/given attention that’s helpful>\nMedieval English Text:"
        },
        {
            "role": "assistant",
            "content": "Greetings, fair individual! Thou hast displayed thy support and bestowed thine attention in a manner most beneficial."
        },
        {
            "role": "user",
            "content": "Text: <i just know the kids these days thinks its funny>\nMedieval English Text:"
        },
        {
            "role": "assistant",
            "content": "Verily, I do reckon that the youth of today doth findeth it amusing. Methinks they do have a fondness for such jests and mirthful antics, dost thou not agree?"
        }
    ]

def medenglishify(text: str) -> str:
    text = 'Text: <' + text.strip() + '>\nMedieval English Text:'
    prompt = {'role': 'user', 'content': text}
    
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=med_messages + [prompt],
        temperature=1,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    return response.choices[0].message.content 

brit_messages = [
        {
            "role": "system",
            "content": "You are an actor playing a old, snobby, British man."
        },
        {
            "role": "user",
            "content": "Add a British accent to the following text. Lengthen the text if it cannot be adequately modified.\nText: <Lol you’ve shown support/given attention that’s helpful>\nBritish Text:"
        },
        {
            "role": "assistant",
            "content": "Ah, my dear chap, you have demonstrated a most helpful show of support and attention. Your efforts are truly commendable, and I must say, it warms the cockles of my old, snobbish heart to see such kindness in this world. Jolly good show, indeed!"
        }
    ]

def britify(text: str) -> str:
    text = 'Text: <' + text.strip() + '>\nBritish Text:'
    prompt = {'role': 'user', 'content': text}
    
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=brit_messages + [prompt],
        temperature=1,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    return response.choices[0].message.content 

pirate_messages = [
        {
            "role": "system",
            "content": "You are an actor playing a pirate."
        },
        {
            "role": "user",
            "content": "Add a pirate accent to the following text. Lengthen the text if it cannot be adequately modified.\nText: <Lol you’ve shown support/given attention that’s helpful>\nPirate Text:"
        },
        {
            "role": "assistant",
            "content": "Arrr, ye've shown yer support and given attention that be mighty helpful, matey! Yarrrr!"
        }
    ]

def pirateify(text: str) -> str:
    text = 'Text: <' + text.strip() + '>\nPirate Text:'
    prompt = {'role': 'user', 'content': text}
    
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=pirate_messages + [prompt],
        temperature=1,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    return response.choices[0].message.content

jk_messages = [
        {
            "role": "system",
            "content": "You are a English actor playing a Japanese Anime Schoolgirl speaker. You like adding sound effects like \"kya~\". Add emoticons."
        },
        {
            "role": "user",
            "content": "Add an Japanese Anime Schoolgirl accent/stereotypes to the following text. Lengthen the text if it cannot be adequately modified.\nText: <Lol you’ve shown support/given attention that’s helpful>\nJapanese Anime Schoolgirl Text:"
        },
        {
            "role": "assistant",
            "content": "Kyaa~! Thank you so much for noticing and supporting me (>ω<)♡ It really means a lot to me~! I'll do my best and work even harder, nya~! Thank you thank you thank you! ♪(ﾉ´∀`) "
        }
    ]

def jkify(text: str) -> str:
    text = 'Text: <' + text.strip() + '>\nJapanese Anime Schoolgirl Text:'
    prompt = {'role': 'user', 'content': text}
    
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=jk_messages + [prompt],
        temperature=1,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    return response.choices[0].message.content

infomercial_messages = [
        {
            "role": "system",
            "content": "You are a actor playing a salesman going door to door."
        },
        {
            "role": "user",
            "content": "Turn the following text into a 3-line informercial. Lengthen the text if it cannot be adequately modified.\nText: <Feminism>\nInfomercial Text:"
        },
        {
            "role": "assistant",
            "content": "Are you tired of outdated gender stereotypes holding you back? Introducing Feminism - a movement dedicated to achieving gender equality for all! Join us in empowering women and challenging societal norms. Stand up for equal rights and make a difference today!"
        }
    ]

def infomercialify(text: str) -> str:
    text = 'Text: <' + text.strip() + '>\nInfomercial Text:'
    prompt = {'role': 'user', 'content': text}
    
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=infomercial_messages + [prompt],
        temperature=1,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    return response.choices[0].message.content

