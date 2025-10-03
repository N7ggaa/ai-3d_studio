-- VideoTo3D Configuration
-- Contains all configurable settings for the plugin

return {
    -- Plugin Information
    PLUGIN_NAME = "Video to 3D",
    VERSION = "1.0.0",
    
    -- UI Settings
    UI = {
        WINDOW_SIZE = Vector2.new(400, 600),
        WINDOW_MIN_SIZE = Vector2.new(300, 300),
        DEFAULT_THEME = "Dark",
        
        -- Colors
        COLORS = {
            Dark = {
                Background = Color3.fromRGB(45, 45, 45),
                Surface = Color3.fromRGB(60, 60, 60),
                Primary = Color3.fromRGB(0, 120, 215),
                PrimaryHover = Color3.fromRGB(0, 100, 180),
                Text = Color3.fromRGB(255, 255, 255),
                TextSecondary = Color3.fromRGB(200, 200, 200),
                TextDisabled = Color3.fromRGB(150, 150, 150),
                Border = Color3.fromRGB(100, 100, 100),
                Card = Color3.fromRGB(60, 60, 60),
                CardHover = Color3.fromRGB(70, 70, 70),
                Error = Color3.fromRGB(255, 100, 100),
                Success = Color3.fromRGB(100, 255, 100)
            },
            Light = {
                Background = Color3.fromRGB(240, 240, 240),
                Surface = Color3.fromRGB(255, 255, 255),
                Primary = Color3.fromRGB(0, 120, 215),
                PrimaryHover = Color3.fromRGB(0, 100, 180),
                Text = Color3.fromRGB(0, 0, 0),
                TextSecondary = Color3.fromRGB(60, 60, 60),
                TextDisabled = Color3.fromRGB(150, 150, 150),
                Border = Color3.fromRGB(200, 200, 200),
                Card = Color3.fromRGB(255, 255, 255),
                CardHover = Color3.fromRGB(245, 245, 245),
                Error = Color3.fromRGB(200, 50, 50),
                Success = Color3.fromRGB(50, 200, 50)
            }
        },
        
        -- Icons
        ICONS = {
            LOGO = "rbxassetid://6031075926",
            PLAY = "rbxassetid://6031075927",
            PAUSE = "rbxassetid://6031075928",
            SETTINGS = "rbxassetid://6031075929"
        }
    },
    
    -- Video Processing
    VIDEO = {
        MAX_DURATION = 30, -- seconds
        FRAME_RATE = 1,    -- frames per second
        MAX_RESOLUTION = Vector2.new(1920, 1080)
    },
    
    -- Model Generation
    MODEL = {
        DEFAULT_SCALE = Vector3.new(1, 1, 1),
        MAX_TRIANGLES = 10000,
        TEXTURE_SIZE = Vector2.new(1024, 1024)
    },
    
    -- Templates
    TEMPLATES = {
        {
            id = "character",
            name = "Character",
            description = "Create a 3D character model",
            icon = "rbxassetid://6031075926",
            settings = {
                frameRate = 2,
                duration = 15
            }
        },
        {
            id = "vehicle",
            name = "Vehicle",
            description = "Create a 3D vehicle model",
            icon = "rbxassetid://6031075930",
            settings = {
                frameRate = 1,
                duration = 30
            }
        },
        {
            id = "building",
            name = "Building",
            description = "Create a 3D building model",
            icon = "rbxassetid://6031075935",
            settings = {
                frameRate = 0.5,
                duration = 30
            }
        }
    },
    
    -- Storage
    STORAGE = {
        SETTINGS_KEY = "VideoTo3D_Settings",
        CACHE_FOLDER = "VideoTo3D_Cache"
    }
}
