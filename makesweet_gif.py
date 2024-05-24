import subprocess
import asyncio
import os

def COMMAND(left_image_path: str, right_image_path: str, output_path: str):
    cwd = os.getcwd()
    return [
        'docker', 'run', '-v', f'{cwd}:/share', 'makesweet',
        '--zip', 'makesweet/templates/heart-locket.zip',
        '--start', '15',
        '--in', left_image_path, right_image_path,
        '--gif', output_path
    ]
    
async def create_heart_locket_gif(left_image_path: str, right_image_path: str, output_path: str):
    process = await asyncio.create_subprocess_exec(*COMMAND(left_image_path, right_image_path, output_path))
    await process.wait()
    return process.returncode