# RedditPaletteBot

This is a small project that I created to show a bit of what I'm able to do with Python.

This is a Reddit bot that listens to a subreddit comments for mention of "palettebot".

Once a mention is found, the bot takes the image URL for the post in which the comment was made, uploads the image to Imagga API to find dominant colors in the image,
and then uses the Python Pillow library to create a stitched image of these colors to create a color palette. This color palette image is then uploaded to Imgur, and
the Imgur image link is retrieved.

The Imagga API is also used to automatically generate tags for the image.

The bot then replies to the comment with the Imgur link, and the automatically generated image tags.

If you'd like to use this bot, you'll have to authenticate via OAuth on the Reddit API. You'll also have to make a free account on Imagga to use their API. Finally,
you'll have to make an Imgur account to use their API.

Feel free to reach out to me at ellis3684@yahoo.com with comments or suggestions on my code!
