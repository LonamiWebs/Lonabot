from actions.action_base import ActionBase
from tokens import load_token

from datetime import datetime, timedelta

import os.path
import requests
import sys

try:
    import youtube_dl
    import youtube_dl.utils

except ImportError:
    pass  # This module won't work

class DownloadAction(ActionBase):
    def __init__(self):
        # Assume that we'll enable the action
        enabled = True

        # First, check that the «youtube_dl» module has loaded
        if 'youtube_dl' not in sys.modules:
            enabled = False

        # Then, check for the token
        else:
            self.token = load_token('YT')
            if self.token is None:
                enabled = False

            else:
                # Ensure we have the directory for downloading files
                self.temp_dir = '../Data/Tmp/YT'
                os.makedirs(self.temp_dir, exist_ok=True)

        # After all the checks, finally initialize the action
        super().__init__(name="DOWNLOAD FROM THE INTERNET",
                         keywords=[r"(?:download|dl) (mp3) (.+)"],
                         enabled=enabled,
                         keyword_match_whole_line=True)

        self.urls = {
            'yt_search': 'https://www.googleapis.com/youtube/v3/search',
            'yt_vidurl': 'https://youtu.be/{}'
        }

        # TODO Should all the commands have a cool-down?
        # And so then we can just do «self.cooldown = timedelta(minutes=1)»
        self.cooldown = timedelta(minutes=5)
        self.last_used = None

    def act(self, data):

        # Ensure we satisfy the cooldown
        if (not data.sender.is_admin and  # Admins just don't care about cooldown
                self.last_used is not None):

            time_diff = datetime.now() - self.last_used
            if time_diff < self.cooldown:
                cooldown_left = self.cooldown - time_diff
                self.send_msg(data, 'this command has {}m {}s left before it cools down, sorry :P'
                              .format(cooldown_left.seconds // 60, cooldown_left.seconds % 60))
                return

            else:
                # Update last use
                self.last_used = datetime.now()

        # TODO Add confirmation, "Is this the song you want? Shall i look for more?"
        # TODO If the file to download is too big, don't download (tg limits to 50mb, maybe I limit to 10mb?)
        type = data.match.group(1)
        name = data.match.group(2)
        self.send_msg(data, 'let me look that up for you...')

        # First, look for the video given the query
        youtube_item = None
        try:
            parameters = {
                'part': 'id,snippet',
                'maxResults': 10,
                'q': name,
                'key': self.token
            }
            result = requests.get(self.urls['yt_search'], params=parameters, timeout=5).json()

            # Iterate over the items until we find one which isn't a channel
            for item in result['items']:
                if item['id']['kind'] == 'youtube#video':
                    youtube_item = item
                    break  # Stop iterating over the items that resulted from our query to YouTube

        except requests.exceptions.ReadTimeout:
            self.send_msg(data, 'sorry it took so long for me to check that i gave up')

        # If we found a video, let's send its audio to the user!
        if youtube_item is not None:

            # Notify that we found this song title
            title = youtube_item['snippet']['title']
            self.send_msg(data, "i found «{}», let me do some stuff and i'll send you the song!".format(title))

            # Retrieve the video ID and set a valid url for later use on download
            video_id = youtube_item['id']['videoId']

            # Check if this file is already in Telegram servers; If so, don't download again
            if data.bot.database.check_file_audio(video_id):
                data.bot.send_audio(data.chat, file_id=video_id)

            else:  # Otherwise download and upload
                file_path, title, artist = self._download_mp3(video_id)

                # The download may fail!
                if file_path is None:
                    self.send_msg(data, "this is embarrassing, i wasn't able to download that song :(")

                else:  # Or may not
                    data.bot.send_audio(data.ori_msg.chat,
                                        file_path=file_path, file_id=video_id,
                                        title=title, artist=artist)

                    # Delete the file after it has been sent
                    os.remove(file_path)



    def _download_mp3(self, youtube_vid_id):
        """
        Downloads a MP3 file given a YouTube video ID
        :param youtube_vid_id: The ID of the YouTube video
        :return: (file_path, title and artist) if the download was successful
        """

        # Set the youtube-dl options (use output in template format)
        # Later, we'll adjust the output not to use the template format and instead
        #        get the real path; but for that we need to download the video!
        output = os.path.join(self.temp_dir, '%(title)s.%(ext)s')
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': output,
            'restrictfilenames': True
        }

        # Let's download the video
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            try:
                # Instead of using «download([video_url])», use «extract_info(video_url)»
                # Both download the video, but the later also retrieves the information
                result = ydl.extract_info(self.urls['yt_vidurl'].format(youtube_vid_id))

                # TODO remove this dirty hack?
                # Instead trying to "guess" where the file was saved, actually retrieve where it was saved!
                title = result['title']
                file_path = os.path.join(self.temp_dir, '{}.mp3'
                                         .format(youtube_dl.utils
                                                 .sanitize_filename(title, restricted=True)))

                # Check if the title is in the «artist - title» format
                if '-' in title:
                    artist = title.split('-')[0].strip()
                    title = title.split('-')[1].strip()

                # Otherwise, fallback to use the uploader name
                # Note that this may not be the real artist
                else:
                    artist = result['uploader']

                return file_path, title, artist

            except ydl.UnavailableVideoError:
                return None, None, None
