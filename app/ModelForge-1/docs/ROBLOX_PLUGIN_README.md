# AI 3D Model Generator for Roblox

A Roblox Studio plugin that generates 3D models from various inputs (text, images, videos) using AI, with automatic LOD generation, Roblox material mapping, and sprite generation.

## 🌟 Features

### Core Features
- **Text-to-3D** - Generate 3D models from text prompts
- **Image-to-3D** - Convert 2D images to 3D models
- **Video-to-3D** - Create 3D models from video frames
- **Sprite Generation** - Create 2D sprites from 3D models or text
- **Auto LOD Generation** - Automatic Level of Detail generation
- **Roblox Material Mapping** - Smart material conversion for Roblox
- **Batch Processing** - Process multiple inputs at once

### Technical Features
- **Modular Architecture** - Easy to extend and maintain
- **Performance Optimized** - Efficient mesh and sprite processing
- **Cross-Platform** - Works on Windows and macOS
- **Developer Friendly** - Well-documented API and examples
- **Test Coverage** - Comprehensive test suite for all components

## 🚀 Quick Start

### Prerequisites
- Roblox Studio
- Python 3.8+
- FFmpeg (for video processing)

### Installation
1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Place the plugin in your Roblox Studio plugins folder
4. Launch Roblox Studio and enable the plugin
- Required Python packages (see `requirements.txt`)

### Installation
1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Install the plugin in Roblox Studio

## 🛠️ Project Structure

```
project_root/
├─ src/             # Core modules and plugin code
├─ tests/           # Unit & integration tests
├─ assets/          # Sample meshes and textures
├─ docs/            # Documentation
├─ configs/         # Configuration files
├─ scripts/         # Utility scripts
└─ outputs/         # Generated assets
```

## 🎨 Sprite Generation

The plugin includes a powerful sprite generation system with the following features:

### Features
- Create sprites from 3D models with custom camera angles
- Generate text sprites with various styles and formatting
- Create sprite sheets from multiple sprites
- Support for different output formats (PNG, JPG)
- Batch processing of sprite generation

### Example Usage
```lua
local SpriteGenerator = require(script.Parent.SpriteGenerator)

-- Create a new sprite generator
local generator = SpriteGenerator.new({
    outputDir = "output/sprites",
    tempDir = "temp",
    defaultSpriteSize = Vector2.new(64, 64)
})

-- Create a colored sprite
local sprite = generator:createColoredSprite("RedSquare", Color3.fromRGB(255, 0, 0), Vector2.new(32, 32))

-- Create a text sprite
local textSprite = generator:createTextSprite("Hello", "Hello, World!", Vector2.new(100, 50))

-- Create a sprite sheet
local spriteSheet = generator:createSpriteSheet({
    name = "CharacterSprites",
    sprites = {sprite, textSprite},
    columns = 2,
    rows = 1,
    padding = 2
})
```

## 🧪 Testing

Run the test suite to verify everything is working correctly:

```bash
lua tests/run_tests.lua
```

### Test Coverage
- Sprite generation and manipulation
- Material mapping
- LOD generation
- Job queue system
- AI model service

## 📚 Documentation

- [API Reference](docs/API.md)
- [Developer Guide](docs/DEVELOPER_GUIDE.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](docs/CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
