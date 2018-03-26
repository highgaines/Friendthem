class YoutubeChannelNotFound(Exception):
    def __str__(self):
        return 'Youtube channel not found for this user.'

