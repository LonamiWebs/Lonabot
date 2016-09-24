import os.path
from io import BytesIO

import requests

from commands.command_base import CommandBase
from utils.tokens import load_token

try:
    import youtube_dl
    import youtube_dl.utils
except ImportError:
    youtube_dl = None  # This module won't work


class Mp3Command(CommandBase):
    """Downloads the specified query or video URL (must start with "http") and returns a .mp3"""

    # Store all the songs which we already have uploaded, not to download them again
    already_uploaded = {}

    @staticmethod
    def get_yt_url(video_id):
        return 'https://youtu.be/{}'.format(video_id)

    def __init__(self):
        # Assume that we'll enable the action
        enabled = True

        # First, check that the «youtube_dl» module has loaded
        if not youtube_dl:
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
        super().__init__(command='mp3',
                         examples=[
                             '/mp3 s3rl ftw',
                             '/mp3 https://youtu.be/vbBfw4c42Zo'
                         ],
                         enabled=enabled)

        self.query_url = 'https://www.googleapis.com/youtube/v3/search'

    def ask_next_confirmation(self, data, from_index, youtube_items):
        """Asks for confirmation on the next available video, whether the user wants it video or not.
           If no video is provided, False is returned"""

        for i in range(from_index, len(youtube_items)):
            item = youtube_items[i]
            if item['id']['kind'] == 'youtube#video':
                # We now have a video item (i.e. not a channel)
                title = item['snippet']['title']

                # Set the thumbnail and the caption
                thumbnail = item['snippet']['thumbnails']['high']['url']
                caption = 'I found «{}». Is this the song you wanted (/yes, /no, /cancel)?'.format(title)

                r = requests.get(thumbnail)
                with BytesIO(r.content) as handle:
                    data.bot.send_photo(data.chat,
                                        file_handle=handle,
                                        caption=caption)

                self.set_pending(data.sender.id, (i, youtube_items))
                return

        self.send_msg(data, 'Sorry, I do not have more videos to show you.')

    def act(self, data):
        if not data.parameter:
            self.show_invalid_syntax(data)
            return

        url = None
        if self.is_pending(data.sender.id):
            item_index, youtube_items = self.get_pending(data.sender.id)

            # Did the user want this video?
            if data.parameter == '/yes':
                # Retrieve the video ID and set a valid url for later use on download
                self.send_msg(data, 'OK, I will send you that song after I prepared it.')
                video_id = youtube_items[item_index]['id']['videoId']
                url = self.get_yt_url(video_id)

            # Did the user wanted a different video?
            elif data.parameter == '/no':
                # + 1 because we want to ask for the next video
                self.ask_next_confirmation(data, item_index + 1, youtube_items)

            # Did the user cancel the operation?
            elif data.parameter == '/cancel':
                self.send_msg(data, 'OK, operation cancelled.')
            else:
                self.send_msg(data, 'Sorry, command not understood! Operation cancelled.')

        # It may be an URL already, or it may be a query
        elif data.parameter.startswith('http'):
            self.send_msg(data, 'Let me prepare some stuff for that URL and I will send you the song.')
            url = data.parameter

        # The user entered a query, so look in YouTube
        else:
            max_results = 10
            # First, look for the video given the query
            try:
                parameters = {
                    'part': 'id,snippet',
                    'maxResults': max_results,
                    'q': data.parameter,
                    'key': self.token
                }
                result = requests.get(self.query_url, params=parameters, timeout=5).json()

                # Ask for confirmation on the next (the first found) video
                self.ask_next_confirmation(data, from_index=0, youtube_items=result['items'])

            except requests.exceptions.ReadTimeout:
                self.send_msg(data, 'Sorry, the request took too long.')

            return

        # If we don't have any URL, no actions were taken; do nothing
        if not url:
            return

        # OK, now we should finally have a valid URL
        # Check if this file is already in Telegram servers; If so, don't download again
        if url in self.already_uploaded:
            data.bot.send_audio(data.chat, tg_id=self.already_uploaded[url])

        else:  # Otherwise download and upload
            file_path, title, artist = self._download_mp3(url)

            # The download may fail due to the file being too large
            if file_path is None:
                self.send_msg(data, 'Sorry, that file is too large.')

            else:
                with open(file_path, 'rb') as file:
                    tg_id = data.bot.send_audio(data.ori_msg.chat,
                                                file_handle=file,
                                                title=title, artist=artist)
                if tg_id:
                    self.already_uploaded[url] = tg_id

                # Delete the file after it has been sent
                os.remove(file_path)

    def _download_mp3(self, url):
        """
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
            'restrictfilenames': False,
            #               MB   KB     Bytes
            'max_filesize': 20 * 1024 * 1024
        }

        # Let's download the video
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            # Instead of using «download([video_url])», use «extract_info(video_url)»
            # Both download the video, but the later also retrieves the information
            result = ydl.extract_info(url)

            # Instead trying to "guess" where the file was saved, actually retrieve where it was saved!
            title = result['title']
            file_path = os.path.join(self.temp_dir, '{}.mp3'
                                     .format(youtube_dl.utils
                                             .sanitize_filename(title)))

            # Check if the file exists, if it doesn't, then it
            # was not downloaded because it was too large
            if not os.path.isfile(file_path):
                return None, None, None

            # Check if the title is in the «artist - title» format
            if '-' in title:
                artist = title.split('-')[0].strip()
                title = title.split('-')[1].strip()

            # Otherwise, fallback to use the uploader name
            # Note that this may not be the real artist
            else:
                artist = result['uploader']

            return file_path, title, artist
