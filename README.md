# x-mcp MCP server

MCP project to connect Claude with X/Twitter for creating and managing posts directly from the chat interface.

## Features
* Create draft tweets and threads
* List all existing drafts
* Publish drafts to X/Twitter
* Delete unwanted drafts
* Direct integration with Claude chat

## Configuration

### Install UV Package Manager
Install UV globally using Homebrew:
```bash
brew install uv
```

### Claude Desktop Configuration
Create or edit the Claude configuration file at:
- MacOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%/Claude/claude_desktop_config.json`

If the file doesn't exist, create it with the following content:
```json
{
  "mcpServers": {
    "x_mcp": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/x-mcp",
        "run",
        "x-mcp"
      ],
      "env": {
        "TWITTER_API_KEY": "your_api_key",
        "TWITTER_API_SECRET": "your_api_secret",
        "TWITTER_ACCESS_TOKEN": "your_access_token",
        "TWITTER_ACCESS_TOKEN_SECRET": "your_access_token_secret"
      }
    }
  }
}
```

Replace `/path/to/x-mcp` with your actual path to the cloned repository.

### Getting X/Twitter API Keys

1. Go to [X API Developer Portal](https://developer.x.com/en/products/x-api)
2. Click on "Developer Portal"
3. Create a new project
4. Navigate to "Projects and Apps"
5. Select your project
6. In "User Authentication Settings":
   - Click "Set up"
   - Select "Read and Write" permissions
   - Choose "Web App, Automated App or Bot" for App Type
   - Set Callback URL/Redirect URL to `http://localhost/`
   - Set Website URL to `http://example.com/`
   - Click "Save"
7. Go to "Keys and Tokens" section:
   - Generate API Key and Secret
   - Generate Access Token and Access Token Secret
   - Copy and store all credentials safely

Replace the placeholder values in `claude_desktop_config.json` with your actual credentials.

## Run Locally

1. Clone the repository:
```bash
git clone https://github.com/yourusername/x-mcp.git
cd x-mcp
```

2. Create and activate virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Unix/macOS
# or
.venv\Scripts\activate  # On Windows
```

3. Install dependencies:
```bash
uv sync
```

## Usage

In your Claude chat, you can now:
* Create a tweet: `Send a tweet saying "Hello, World!"`
* Create a thread: `Create a thread about [topic]`
* List drafts: `Show me all draft tweets`
* Publish draft: `Publish draft [draft_id]`
* Delete draft: `Delete draft [draft_id]`

## Troubleshooting

If you encounter issues:

1. UV Installation: If the server isn't working, it might be because UV was installed locally via pip instead of globally. To fix this:
   - Uninstall UV: `pip uninstall uv`
   - Install globally using Homebrew: `brew install uv`
   - OR find your UV path: `which uv`
   - Replace `"command": "uv"` with `"command": "/your/uv/path"` in `claude_desktop_config.json`

2. Make sure all X/Twitter API credentials are correctly set in the configuration file

3. Verify the path to x-mcp in your configuration matches your actual repository location

4. Ensure you've activated the virtual environment before running UV commands

## Development

For debugging, use the MCP Inspector:
```bash
npx @modelcontextprotocol/inspector uv --directory /path/to/x-mcp run x-mcp
```