import discord
import os, sys
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
from random import randint
# from selenium import webdriver
import imageio
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
import moviepy.editor as mp
import time

# from PIL import Image

def get_video_URL(search_key=None):
    if search_key:
        URL = "https://www.pornhub.com/gifs/search?search=" + search_key + "&page=" + str(randint(1,2))
    else:
        URL = "https://www.pornhub.com/gifs?page=" + str(randint(1,5))

    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')
    gifs = soup.find_all(class_='gifVideoBlock js-gifVideoBlock')
    num = randint(0, len(gifs)-1)
    gif = gifs[num]
    gif_url = "https://www.pornhub.com" + str(gif.find('a').get('href'))

    return gif_url

def download_video(url):
    filename = '/assets/asset'
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    video_url = soup.find('div', id='js-gifToWebm', class_="centerImage notModal")['data-mp4']
    r = requests.get(video_url)
    curr_path = str(os.path.dirname(os.path.abspath(__file__)))
    open(curr_path + filename + '.mp4', 'wb').write(r.content)

    # Trim it to 1.5s
    targetname = curr_path + filename + '_trimmed' + '.mp4'
    ffmpeg_extract_subclip((curr_path+filename+'.mp4'), 0, 1.5, targetname=targetname)

    # Resize it to max_height = 360
    clip = mp.VideoFileClip(targetname)
    clip_resized = clip.resize(height=240) # make the height 360px ( According to moviePy documenation The width is then computed so that the width/height ratio is conserved.)
    clip_resized.write_videofile(curr_path + filename + '_resized' + '.mp4')

    return filename+'_resized'


def convert_mp4_gif(filename):
    inputpath = str(os.path.dirname(os.path.abspath(__file__))) + filename + '.mp4'
    outputpath = str(os.path.dirname(os.path.abspath(__file__))) + os.path.splitext(filename)[0] + '.gif'
    reader = imageio.get_reader(inputpath)
    fps = 12
    
    writer = imageio.get_writer(outputpath, fps=fps)
    for i,im in enumerate(reader):
        writer.append_data(im)
    writer.close()
    return outputpath

client = discord.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("-e") and message.content == '-e':
        await message.channel.send("Hi! I am **Educ4tor's Educ4tive Bot**!\nPlease use \"-e help\" for help utility!")

    if message.content.startswith('-e help'):
        await message.channel.send("Welcome to **Educ4tor's Educ4tive Bot** help utility!\n\n - To request a random GIF: \"-e gif\"\n - To request a specified GIF: \"-e gif $\{Name\}\"  (e.g. -e gif Leah Gotti)")

    if message.content.startswith('-e gif'):
        # Set the maximum number of tries
        num_retry = 0
        search_key = None

        # Random GIF
        if message.content == '-e gif':
            await message.channel.send('Got your order boss! Retrieving a random top-rated GIF in progress..\n')

        # Specified GIF
        else:
            search_key_list = message.content.split(' ')[2:]
            search_key = ""
            display_key = ""
            for key in search_key_list:
                search_key += (key + '+')
                display_key += (key + ' ')
            search_key = search_key[0:(len(search_key)-1)] 
            display_key = display_key[0:(len(display_key)-1)] 
            await message.channel.send('Got your order boss! Retrieving %s GIF in progress..\n' % display_key)
        
        # This loop will break only if the GIP is sent out
        while True:
            try:  
                # Get a random video url
                if search_key:
                    video_url = get_video_URL(search_key)
                else:
                    video_url = get_video_URL()

                # Download, trim and resize the video
                filename = download_video(video_url)

                # Convert the video into GIF
                filename = convert_mp4_gif(filename)

                # Send the GIF to discord channel
                msg = await message.channel.send(file=discord.File(filename))

                # Delete the GIF after 5s
                await message.channel.send('Activate self-destruction in 5s!\n')
                time.sleep(5)
                await msg.delete()
                await message.channel.send('Thanks for watching!\n')

            except:
                await message.channel.send('Something went wrong! Retrying...\n')

                # When any of the steps fails, retry and add 1 to num_retries
                num_retry += 1

                # If num_retry > 5, abort.
                if num_retry > 5:
                    await message.channel.send('Bot is sick :( Contact Educ4tor!\n')
                    break

                continue

            # Remove the files from the local
            abs_path = str(os.path.dirname(os.path.abspath(__file__)))
            os.remove(abs_path+'/assets/asset.mp4')        
            os.remove(abs_path+'/assets/asset_resized.mp4')  
            os.remove(abs_path+'/assets/asset_trimmed.mp4')  
            os.remove(abs_path+'/assets/asset_resized.gif')  
            break

# Load the .env since the original one does not work
load_dotenv()
client.run(os.getenv('TOKEN'))
