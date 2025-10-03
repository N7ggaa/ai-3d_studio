# Prompt2Roblox Plugin

A Roblox Studio plugin that connects to the Prompt2Roblox backend to process YouTube videos and generate Roblox assets.

## Installation

1. Build the plugin into a `.rbxm` file:
   ```bash
   rojo build -o Prompt2Roblox.rbxm
   ```

2. In Roblox Studio:
   - Go to the `Plugins` tab
   - Click on the `Plugins Folder` button
   - Copy the `Prompt2Roblox.rbxm` file into the plugins folder
   - Restart Roblox Studio or use `Reload Plugins`

## Usage

1. Click the Prompt2Roblox button in the Plugins tab
2. Enter a YouTube URL and an optional prompt
3. Click "Process Video"
4. The plugin will connect to your local backend and process the video

## Development

### Prerequisites

- [Rojo](https://rojo.space/) for building the plugin
- A running instance of the Prompt2Roblox backend

### Building

```bash
rojo build -o Prompt2Roblox.rbxm
```

### Directory Structure

- `Prompt2Roblox.lua` - Main plugin script
- `Widget.lua` - UI components
- `init.lua` - Plugin entry point
- `README.md` - This file

## License

MIT
