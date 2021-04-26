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

# from PIL import Image

def get_random_video_URL():
    URL = "https://www.pornhub.com/gifs?o=tr"
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')
    gifs = soup.find_all(class_='gifVideoBlock js-gifVideoBlock')
    random_num = randint(0, len(gifs)-1)
    random_gif = gifs[random_num]
    random_gif_url = "https://www.pornhub.com" + str(random_gif.find('a').get('href'))

    return random_gif_url

def download_random_video(url):
    filename = '/random/random'
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
        sys.stdout.write("\rframe {0}".format(i))
        sys.stdout.flush()
        writer.append_data(im)
    writer.close()
    print("Done.")
    return outputpath

client = discord.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('-e help'):
        await message.channel.send("Welcome to Educ4tor's Educ4ting Bot help utility!\n\n - To request a random GIF: \"-e gif\"")

    
    if message.content.startswith('-e gif'):
        # Random GIF
        if message.content == '-e gif':
            await message.channel.send('Retrieving the top-rated random GIF!\n')

            # Get a random video url
            random_video_url = get_random_video_URL()
            filename = download_random_video(random_video_url)
            filename = convert_mp4_gif(filename)


            await message.channel.send(file=discord.File(filename))

            abs_path = str(os.path.dirname(os.path.abspath(__file__)))
            os.remove(abs_path+'/random/random.mp4')        
            os.remove(abs_path+'/random/random_resized.mp4')  
            os.remove(abs_path+'/random/random_trimmed.mp4')  
            os.remove(abs_path+'/random/random_resized.gif')  

load_dotenv()
client.run(os.getenv('TOKEN'))
