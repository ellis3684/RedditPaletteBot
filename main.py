import praw
import requests
from PIL import Image
from imgurpython import ImgurClient
import os

REDDIT_CLIENT_ID = os.environ["REDDIT_CLIENT_ID"]
REDDIT_CLIENT_SECRET = os.environ["REDDIT_CLIENT_SECRET"]
REDDIT_USERNAME = os.environ["REDDIT_USERNAME"]
REDDIT_PASSWORD = os.environ["REDDIT_PASSWORD"]

IMAGGA_API_KEY = os.environ["IMAGGA_API_KEY"]
IMAGGA_API_SECRET = os.environ["IMAGGA_API_SECRET"]

IMGUR_CLIENT_ID = os.environ["IMGUR_CLIENT_ID"]
IMGUR_CLIENT_SECRET = os.environ["IMGUR_CLIENT_SECRET"]


def create_palette_image(*images):
    """This function takes images as arguments, and then stitches them together to create a color palette."""
    total_width = 0
    list_of_images = []
    for image in images:
        (width, height) = image.size
        total_width += width
        total_height = height
        list_of_images.append(image)

    palette_image = Image.new('RGB', (total_width, total_height))

    paste_width = 0
    for n in range(len(images)):
        palette_image.paste(im=images[n], box=(paste_width, 0))
        (width, height) = images[n].size
        paste_width += width

    return palette_image


def process_image(reddit_image_url):
    """
    This function takes an image as an argument, creates a color palette image of the five most prominent colors
    from that image, also creates a list of tags that describe the image, then returns these two values in the form
    of an imgur link, and a list of tags.
    :param reddit_image_url: The url taken from the Reddit post of the comment which we're going to respond to. This
    argument could be any image though.
    :return: Two values: the imgur link of the color palette image; and the list of tags that describes
    the Reddit image.
    """
    palette_parameters = {
        "image_url": reddit_image_url,
        "extract_object_colors": 0,
    }
    palette_response = requests.get(
        "https://api.imagga.com/v2/colors",
        params=palette_parameters,
        auth=(IMAGGA_API_KEY, IMAGGA_API_SECRET)
    )
    palette_data = palette_response.json()
    colors_info = palette_data["result"]["colors"]["image_colors"]
    hex_colors = [color["closest_palette_color_html_code"] for color in colors_info]
    images = []
    for color in hex_colors:
        images.append(Image.new(mode="RGB", size=(150, 125), color=color))

    new = create_palette_image(*images)
    new.save("palette-image.jpg")

    tag_parameters = {
        "image_url": reddit_image_url,
    }

    tag_response = requests.get(
        "https://api.imagga.com/v2/tags",
        params=tag_parameters,
        auth=(IMAGGA_API_KEY, IMAGGA_API_SECRET)
    )
    tag_data = tag_response.json()
    tags = tag_data["result"]["tags"]
    tag_list = []
    for tag in tags[:5]:
        tag_description = tag["tag"]["en"]
        tag_list.append(tag_description)

    client = ImgurClient(IMGUR_CLIENT_ID, IMGUR_CLIENT_SECRET)

    response = client.upload_from_path(path="palette-image.jpg")
    get_imgur_link = response["link"]

    return get_imgur_link, tag_list


reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    user_agent="console:COLOR:1.0",
    username=REDDIT_USERNAME,
    password=REDDIT_PASSWORD
)

# Choose the subreddit for the bot to listen to.
subreddit = reddit.subreddit("Damnthatsinteresting")

# Listen to stream of comments in a given subreddit. If a comment mentions 'palettebot' then
# the bot will reply with the color palette imgur link, and a list of descriptive tags in a comment reply.
for comment in subreddit.stream.comments(skip_existing=True):
    if hasattr(comment, "body") and hasattr(comment, "link_url"):
        if "palettebot" in comment.body.lower():
            image_url = comment.link_url
            processed_image = process_image(image_url)
            imgur_link = processed_image[0]
            list_of_tags = processed_image[1]
            image_tags = ', '.join(list_of_tags)
            comment.reply(f"Hey there! I'm a bot that extracts a color palette from an image.\n\n"
                          f"You can access the palette for this image here:\n{imgur_link}\n\nI also take a guess at"
                          f" descriptive tags for the given image.\n\nI would use the following"
                          f" tags to describe this picture:\n{image_tags}.")
            print(f"Reply made! Check out the link titled \"{comment.link_title}\"")
