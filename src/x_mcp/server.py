import os
import json
import logging
import asyncio
from datetime import datetime
from typing import Any, Sequence
from dotenv import load_dotenv
import tweepy
from mcp.server import Server
from mcp.types import (
    Tool,
    TextContent,
    LoggingLevel,
    EmptyResult,
)

# Load environment variables from .env file
load_dotenv()

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("x_mcp")

# Get Twitter API credentials from environment variables
API_KEY = os.getenv("TWITTER_API_KEY")
API_SECRET = os.getenv("TWITTER_API_SECRET")
ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

if not all([API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET]):
    raise ValueError("Twitter API credentials are required")

# Initialize Tweepy client (OAuth 2.0 for token generation + API for media uploads)
client = tweepy.Client(
    consumer_key=API_KEY,
    consumer_secret=API_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET
)

auth = tweepy.OAuth1UserHandler(
    consumer_key=API_KEY,
    consumer_secret=API_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET
)

# API instance for media uploads
api = tweepy.API(auth)

server = Server("x_mcp")

# List available tools
@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools for interacting with Twitter/X."""
    return [
        Tool(
            name="create_draft_tweet",
            description="Create a draft tweet",
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "The content of the tweet",
                    },
                },
                "required": ["content"],
            },
        ),
        Tool(
            name="create_draft_thread",
            description="Create a draft tweet thread",
            inputSchema={
                "type": "object",
                "properties": {
                    "contents": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "An array of tweet contents for the thread",
                    },
                },
                "required": ["contents"],
            },
        ),
        Tool(
            name="list_drafts",
            description="List all draft tweets and threads",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
        Tool(
            name="publish_draft",
            description="Publish a draft tweet or thread",
            inputSchema={
                "type": "object",
                "properties": {
                    "draft_id": {
                        "type": "string",
                        "description": "ID of the draft to publish",
                    },
                },
                "required": ["draft_id"],
            },
        ),
        Tool(
            name="delete_draft",
            description="Delete a draft tweet or thread",
            inputSchema={
                "type": "object",
                "properties": {
                    "draft_id": {
                        "type": "string",
                        "description": "ID of the draft to delete",
                    },
                },
                "required": ["draft_id"],
            },
        ),
        Tool(
            name="upload_media_and_tweet",
            description="Upload a media file (GIF/PNG/JPEG etc.) and create a tweet draft",
            inputSchema={
                "type": "object",
                "properties": {
                    "media_path": {
                        "type": "string",
                        "description": "The file path of the media to upload",
                    },
                    "tweet_text": {
                        "type": "string",
                        "description": "The text content of the tweet",
                    },
                },
                "required": ["media_path", "tweet_text"],
            },
        ),
    ]

@server.call_tool()
async def call_tool(name: str, arguments: Any) -> Sequence[TextContent]:
    """Handle tool calls for creating Twitter/X drafts."""
    if name == "create_draft_tweet":
        return await handle_create_draft_tweet(arguments)
    elif name == "create_draft_thread":
        return await handle_create_draft_thread(arguments)
    elif name == "list_drafts":
        return await handle_list_drafts(arguments)
    elif name == "publish_draft":
        return await handle_publish_draft(arguments)
    elif name == "delete_draft":
        return await handle_delete_draft(arguments)
    elif name == "upload_media_and_tweet":
        return await handle_upload_media_and_tweet(arguments)
    else:
        raise ValueError(f"Unknown tool: {name}")

async def upload_media(file_path: str) -> str:
    """
    Upload media to Twitter and return the media ID.
    - file_path: Path to the media file
    """
    try:
        media = api.media_upload(file_path)
        return media.media_id_string
    except tweepy.TweepyException as e:
        logger.error(f"Twitter API error during media upload: {e}")
        raise RuntimeError(f"Media upload error: {e}")

async def handle_create_draft_tweet(arguments: Any) -> Sequence[TextContent]:
    """
    Create a draft for a regular text tweet and save it to a file.
    - arguments: {"content": "<tweet content>"}
    """
    if not isinstance(arguments, dict) or "content" not in arguments:
        raise ValueError("Invalid arguments for create_draft_tweet")
    content = arguments["content"]
    try:
        draft = {"content": content, "timestamp": datetime.now().isoformat()}
        os.makedirs("drafts", exist_ok=True)
        draft_id = f"draft_{int(datetime.now().timestamp())}.json"
        with open(os.path.join("drafts", draft_id), "w") as f:
            json.dump(draft, f, indent=2)
        logger.info(f"Draft tweet created: {draft_id}")
        return [
            TextContent(
                type="text",
                text=f"Draft tweet created with ID {draft_id}",
            )
        ]
    except Exception as e:
        logger.error(f"Error creating draft tweet: {str(e)}")
        raise RuntimeError(f"Error creating draft tweet: {str(e)}")

async def handle_create_draft_thread(arguments: Any) -> Sequence[TextContent]:
    """
    Create a draft for a thread of multiple tweets and save it to a file.
    - arguments: {"contents": ["tweet1","tweet2",...]}
    """
    if not isinstance(arguments, dict) or "contents" not in arguments:
        raise ValueError("Invalid arguments for create_draft_thread")
    contents = arguments["contents"]
    if not isinstance(contents, list) or not all(isinstance(item, str) for item in contents):
        raise ValueError("Invalid contents for create_draft_thread")
    try:
        draft = {"contents": contents, "timestamp": datetime.now().isoformat()}
        os.makedirs("drafts", exist_ok=True)
        draft_id = f"thread_draft_{int(datetime.now().timestamp())}.json"
        with open(os.path.join("drafts", draft_id), "w") as f:
            json.dump(draft, f, indent=2)
        logger.info(f"Draft thread created: {draft_id}")
        return [
            TextContent(
                type="text",
                text=f"Draft thread created with ID {draft_id}",
            )
        ]
    except Exception as e:
        logger.error(f"Error creating draft thread: {str(e)}")
        raise RuntimeError(f"Error creating draft thread: {str(e)}")

async def handle_list_drafts(arguments: Any) -> Sequence[TextContent]:
    """
    List all tweet and thread drafts saved in the drafts directory.
    """
    try:
        drafts = []
        if os.path.exists("drafts"):
            for filename in os.listdir("drafts"):
                filepath = os.path.join("drafts", filename)
                with open(filepath, "r") as f:
                    draft = json.load(f)
                drafts.append({"id": filename, "draft": draft})
        return [
            TextContent(
                type="text",
                text=json.dumps(drafts, indent=2),
            )
        ]
    except Exception as e:
        logger.error(f"Error listing drafts: {str(e)}")
        raise RuntimeError(f"Error listing drafts: {str(e)}")

async def handle_publish_draft(arguments: Any) -> Sequence[TextContent]:
    """
    Publish a draft to Twitter.
    - Determines whether it's a single tweet or thread based on the draft content.
    """
    if not isinstance(arguments, dict) or "draft_id" not in arguments:
        raise ValueError("Invalid arguments for publish_draft")
    
    draft_id = arguments["draft_id"]
    filepath = os.path.join("drafts", draft_id)
    
    if not os.path.exists(filepath):
        raise ValueError(f"Draft {draft_id} does not exist")
    
    try:
        with open(filepath, "r") as f:
            draft = json.load(f)
        
        # Single tweet
        if "content" in draft:
            content = draft["content"]
            media_ids = None
            
            # Regular draft with media path (images etc.)
            if "media_path" in draft:
                media_id = await upload_media(draft["media_path"])
                media_ids = [media_id]
            # Case where media ID is directly included (including GIFs)
            elif "media_id" in draft:
                media_ids = [draft["media_id"]]
                
            response = client.create_tweet(text=content, media_ids=media_ids)
            tweet_id = response.data['id']
            logger.info(f"Published tweet ID {tweet_id}")
            
            # Delete draft file after posting is complete
            os.remove(filepath)
            
            return [
                TextContent(
                    type="text",
                    text=f"Draft {draft_id} published as tweet ID {tweet_id}",
                )
            ]
        
        # Thread
        elif "contents" in draft:
            contents = draft["contents"]
            last_tweet_id = None
            for content in contents:
                if last_tweet_id is None:
                    response = client.create_tweet(text=content)
                else:
                    response = client.create_tweet(text=content, in_reply_to_tweet_id=last_tweet_id)
                last_tweet_id = response.data['id']
                # Sleep to avoid rate limits
                await asyncio.sleep(1)
            
            logger.info(f"Published thread starting with tweet ID {last_tweet_id}")
            os.remove(filepath)
            
            return [
                TextContent(
                    type="text",
                    text=f"Draft {draft_id} published as thread starting with tweet ID {last_tweet_id}",
                )
            ]
        else:
            raise ValueError(f"Invalid draft format for {draft_id}")
    except tweepy.TweepyException as e:
        logger.error(f"Twitter API error: {e}")
        raise RuntimeError(f"Error publishing draft {draft_id}: {e}")
    except Exception as e:
        logger.error(f"Error publishing draft {draft_id}: {str(e)}")
        raise RuntimeError(f"Error publishing draft {draft_id}: {str(e)}")

async def handle_upload_media_and_tweet(arguments: Any) -> Sequence[TextContent]:
    """
    Upload a generic media file (GIF/PNG/JPEG etc.) and create a draft tweet with it.
    - arguments: {"media_path": "<media file path>", "tweet_text": "<tweet text>"}
    """
    if not isinstance(arguments, dict) or "media_path" not in arguments or "tweet_text" not in arguments:
        raise ValueError("Invalid arguments for upload_media_and_tweet")
    
    media_path = arguments["media_path"]
    tweet_text = arguments["tweet_text"]
    
    if not os.path.exists(media_path):
        raise ValueError(f"Media file {media_path} does not exist")
    
    try:
        # Upload media to Twitter
        media = api.media_upload(filename=media_path)
        media_id = media.media_id_string
        
        # Create draft
        draft = {
            "content": tweet_text,
            "media_id": media_id,
            "timestamp": datetime.now().isoformat()
        }
        
        # Create drafts directory
        os.makedirs("drafts", exist_ok=True)
        
        # Save draft file
        draft_id = f"media_draft_{int(datetime.now().timestamp())}.json"
        with open(os.path.join("drafts", draft_id), "w") as f:
            json.dump(draft, f, indent=2)
        
        logger.info(f"Draft tweet with media created: {draft_id}")
        
        return [
            TextContent(
                type="text",
                text=(
                    f"Draft tweet with media created with ID {draft_id}\n"
                    f"Preview:\nText: {tweet_text}\nMedia: {media_path}\n\n"
                    f"Use publish_draft with this ID to post the tweet."
                ),
            )
        ]
    except tweepy.TweepyException as e:
        logger.error(f"Twitter API error: {e}")
        error_details = str(e)
        return [
            TextContent(
                type="text",
                text=f"Error creating draft tweet with media: {error_details}",
            )
        ]
    except Exception as e:
        logger.error(f"Error creating draft tweet with media: {str(e)}")
        raise RuntimeError(f"Error creating draft tweet with media: {str(e)}")

async def handle_delete_draft(arguments: Any) -> Sequence[TextContent]:
    """
    Delete a specific draft file.
    - arguments: {"draft_id": "<draft file name>"}
    """
    if not isinstance(arguments, dict) or "draft_id" not in arguments:
        raise ValueError("Invalid arguments for delete_draft")
    
    draft_id = arguments["draft_id"]
    filepath = os.path.join("drafts", draft_id)
    
    try:
        if not os.path.exists(filepath):
            raise ValueError(f"Draft {draft_id} does not exist")
        
        os.remove(filepath)
        logger.info(f"Deleted draft: {draft_id}")
        
        return [
            TextContent(
                type="text",
                text=f"Successfully deleted draft {draft_id}",
            )
        ]
    except Exception as e:
        logger.error(f"Error deleting draft {draft_id}: {str(e)}")
        raise RuntimeError(f"Error deleting draft {draft_id}: {str(e)}")

async def main():
    import mcp
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
