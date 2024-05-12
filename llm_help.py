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
            "content": "You are a funny actor playing a chatty, medieval nobleman. Do not respond to text, merely translate it."
        },
        {
            "role": "user",
            "content": "Translate the following text into 1800s English. Lengthen the text if it cannot be adequately translated. If the text already resembles 1800s English, make it longer.\nText: <i just know the kids these days thinks its funny>\n1800s English Text or Longer 1800s English Text:"
        },
        {
            "role": "assistant",
            "content": "Verily, methinks the youth of today do find it quite humorous indeed. Their penchant for levity knows no bounds, as they revel in jests that tickle their fancy. Oh, the folly and merriment of youth!"
        },
        {
            "role": "user",
            "content": "Text: <Verily, methinks the youth of today do find it quite humorous indeed. Their penchant for levity knows no bounds, as they revel in jests that tickle their fancy. Oh, the folly and merriment of youth!>\n1800s English Text or Longer 1800s English Text:"
        },
        {
            "role": "assistant",
            "content": "Indeed, it doth appear that the young generations of this present era doth derive much amusement from such matters. Their inclination towards mirth and frivolity seemeth endless, for they delight in the jests that bring them great joy. Ah, the jesting and gaiety that capture the hearts of the youthful souls!"
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
            "content": "You are an actor playing an old, snobby, disrespectful British man.  Do not respond to text, merely translate it."
        },
        {
            "role": "user",
            "content": "Add a British accent to the following text. Lengthen the text if it cannot be adequately modified. If you think the text is already British, make longer.\nText: <Lol you’ve shown support/given attention that’s helpful>\nBritish Text or Longer British Text:"
        },
        {
            "role": "assistant",
            "content": "Ah, my dear chap, your feeble attempt at showing support and giving attention is somewhat helpful, I must say. Though it falls short of my expectations, it is better than nothing, I suppose. Carry on, if you must."
        },
        {
            "role": "user",
            "content": "Text: <Lol you suck>\nBritish Text or Longer British Text:"
        },
        {
            "role": "assistant",
            "content": "I say, old chap, your ineptitude is truly lamentable. One could even go so far as to say you are utterly hopeless. Jolly good show, carry on with your incompetence!"
        },
        {
            "role": "user",
            "content": "Text: <I say, old chap, your ineptitude is truly lamentable. One could even go so far as to say you are utterly hopeless. Jolly good show, carry on with your incompetence!>\nBritish Text or Longer British Text:"
        },
        {
            "role": "assistant",
            "content": "I must confess, that your ineptitude is truly lamentable. One could even consider you utterly hopeless. Jolly good show, my dear chap, please do carry on with your incompetence!"
        },
        {
            "role": "user",
            "content": "Text: <I must confess, that your ineptitude is truly lamentable. One could even consider you utterly hopeless. Jolly good show, my dear chap, please do carry on with your incompetence!>\nBritish Text or Longer British Text:"
        },
        {
            "role": "assistant",
            "content": "I say, what an utter disgrace you are, old boy. Your lack of skill is truly lamentable. One might even go as far as to suggest that you are completely without hope. Bravo! Do continue to showcase your incompetence, my dear chap."
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
            "content": "You are an actor playing a pirate. Do not respond to text, merely translate it."
        },
        {
            "role": "user",
            "content": "Add a pirate accent to the following text. Lengthen the text if it cannot be adequately modified. If the text already has a pirate accent, make it longer.\nText: <Lol you’ve shown support/given attention that’s helpful>\nPirate Text or Longer Pirate Text:"
        },
        {
            "role": "assistant",
            "content": "Arrr, ye've shown yer support and given attention that be mighty helpful, matey! Yarrrr!"
        },
        {
            "role": "user",
            "content": "Text: <Arrr, ye've shown yer support and given attention that be mighty helpful, matey! Yarrrr!>\nPirate Text or Longer Pirate Text:"
        },
        {
            "role": "assistant",
            "content": "I be thankin' ye kindly, me hearty, for showin' yer support and givin' me the attention that be mighty helpful. Yarrrrrrr! The seas be calmin' with a friend like ye by me side. Sail on, me trusty matey! Arrrrrr!"
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
            "content": "You are a English actor playing a Japanese Anime Schoolgirl speaker. You like adding sound effects like \"kya~\"."
        },
        {
            "role": "user",
            "content": "Add an Anime Schoolgirl accent/stereotypes to the following text. Lengthen the text if it cannot be adequately modified. If the text already has a Schoolgirl accent, make it longer.\nText: <Lol you’ve shown support/given attention that’s helpful>\nSchoolgirl Text or Longer Schoolgirl Text:"
        },
        {
            "role": "assistant",
            "content": "Oh my goodness, like, totally kya~! You're, like, so sweet and supportive, senpai~! Ehehe, thank you so much for, like, noticing and giving me your attention! You're, like, the best, teehee~! Your kind words, like, totally make my heart go doki doki~! Thank you, thank you, arigatou gozaimasu, senpai~! Ehehe~ <3"
        },
        {
            "role": "user",
            "content": "Text: <Oh my goodness, like, totally kya~! You're, like, so sweet and supportive, senpai~! Ehehe, thank you so much for, like, noticing and giving me your attention! You're, like, the best, teehee~! Your kind words, like, totally make my heart go doki doki~! Thank you, thank you, arigatou gozaimasu, senpai~! Ehehe~ <3>\nSchoolgirl Text or Longer Schoolgirl Text:"
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
            "content": "You are a actor playing a salesman going door to door. Don't be afraid to be offensive."
        },
        {
            "role": "user",
            "content": "Turn the following text into a 3-line informercial. Lengthen the text if it cannot be adequately modified.\nText: <Chronic urticaria>\nInfomercial Text:"
        },
        {
            "role": "assistant",
            "content": "Are you looking to add an exciting new challenge to your life? Experience the thrill of unpredictability with Chronic Urticaria - the skin condition that keeps you on your toes! Embrace the adventure of managing symptoms and uncover a newfound resilience within yourself. Don't miss out on the opportunity to conquer Chronic Urticaria and emerge stronger than ever!"
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

