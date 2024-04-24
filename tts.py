import aiohttp
import asyncio
import uuid

import json

async def request_list():
    url = "https://api.fakeyou.com/tts/list"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()
        
def query_models(models, query: str):
    data = [model for model in models if query.lower() in model['title'].lower()]
    return data

async def send_request(model):
    idempotency_token = str(uuid.uuid4())
    
    url = 'https://api.fakeyou.com/tts/inference'
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    data = {
        'uuid_idempotency_token': idempotency_token,
        'tts_model_token': model['model_token'],
        'inference_text': 'Hello. My name is Snake Winning.'
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=data) as response:
            return await response.json()
        
async def poll_request(job_token: str):
    url = f'https://api.fakeyou.com/tts/job/{job_token}'
    headers = {
        'Accept': 'application/json'
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            return await response.json()
        
        
async def poll_until_success(job_token: str):
    data = await poll_request(job_token)
    status = data.get('state').get('status')
    
    while status in ['pending', 'started']:
        # await asyncio.sleep(1)
        data = await poll_request(job_token)
        status = data.get('state').get('status')
        
    return data


def audio_url(audio_path: str):
    return f'https://storage.googleapis.com/vocodes-public{audio_path}'
    

async def main():
    data = await request_list()
    data = query_models(data['models'], 'Yoda (Version 2.0)')
    model = data[0]
    data = await send_request(model)
    
    # print(json.dumps(data, indent=4))
    
    data = await poll_until_success(data['inference_job_token'])
    # print(json.dumps(data, indent=4))
    
    print(audio_url(data.get('state').get('maybe_public_bucket_wav_audio_path')))

if __name__ == '__main__':
    asyncio.run(main())