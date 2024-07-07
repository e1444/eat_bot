import discord
import nltk
import os

# keys
EAT_BOT_TOKEN = os.environ.get('EAT_BOT_TOKEN')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
GOOGLE_CSE_ID = os.environ.get('GOOGLE_CSE_ID')
YOUTUBE_ID = os.environ.get('GOOGLE_EMAIL')
YOUTUBE_PW = os.environ.get('GOOGLE_EMAIL_PW')

# load corpus
try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')

EXTENSIONS = ('extensions.snake', 
              'extensions.misc', 
              'extensions.shark', 
              'extensions.eat', 
            #   'extensions.music', 
              'extensions.old_music', 
            #   'extensions.tts', 
              'extensions.america',
              'extensions.automsg',
              'extensions.makesweet_ext')

GUILDS = [discord.Object(id=1223665705048735846), discord.Object(id=1220725949323022336), discord.Object(id=1147644134312652840), discord.Object(id=1221631514484150342)]
ADMIN_ID = 319162137392054272

RANDOM_ENCOUNTER_PERIOD = 500

# file paths
COUNTER_PATH = 'data/count.json'
JOKE_PATH = 'data/dad_jokes.csv' # taken from https://www.kaggle.com/datasets/usamabuttar/dad-jokes
SG_PATH = 'snake_gatcha/inventories.json'
DEBT_PATH = 'data/debt.json'
AUTOMSG_PATH = 'data/automsg.json'
TTS_HISTORY_PATH = 'data/tts_history.json'

# colours
C_GRAY = '\u001b[0;30m'
C_RED = '\u001b[0;31m'
C_GREEN = '\u001b[0;32m'
C_YELLOW = '\u001b[0;33m'
C_BLUE = '\u001b[0;34m'
C_PINK = '\u001b[0;35m'
C_CYAN = '\u001b[0;36m'
C_WHITE = '\u001b[0;37m'
C_END = '\u001b[0;0m'

# LLM
def PROMPT(noun: str, defn: str) -> str:
    return f"""Characters: @p1, @p2
Background: @p2 is the personification "{noun}", defined as "{defn}"
Prompt: Generate a short conversation starting with @p2 introducing themself. End with @p1 eating @p2.
"""

SYSTEM_PROMPT = 'You are a scriptwriter with a dark sense of humour.'