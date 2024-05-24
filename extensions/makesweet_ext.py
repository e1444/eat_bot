import discord
from discord.ext import commands
from discord import app_commands

from bot import Bot

from makesweet_gif import create_heart_locket_gif
from textgen import centered_text_image
from image_help import download_image, save_image

from constants import *

class MakesweetCog(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot: Bot = bot
        
        print('---\tMakesweetCog loaded\t---')
        
    @app_commands.command(
        name='makesweet',
        description='My beloved'
    )
    async def makesweet(self, ctx: discord.Interaction, *, image_url: str, text: str):
        await ctx.response.defer()
        
        left_img_fp = f'makesweet_cache/{1}.png'
        image_bytes = download_image(image_url)
        save_image(image_bytes, left_img_fp)
        
        right_img_fp = f'makesweet_cache/{2}.png'
        centered_text_image(text, right_img_fp)
        
        out_fp = f'makesweet_cache/{3}.gif'
        ret = await create_heart_locket_gif(left_img_fp, right_img_fp, out_fp)
        
        
        if ret == 0:
            await ctx.followup.send(file=discord.File(out_fp))
        else:
            await ctx.followup.send('An error occurred')
        
        
async def setup(bot: Bot):
    await bot.add_cog(MakesweetCog(bot))