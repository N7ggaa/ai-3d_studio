-- AssetImporter Configuration

local Config = {}

-- Supported file extensions
Config.FILE_EXTENSIONS = {
    IMAGES = {"png", "jpg", "jpeg", "webp", "bmp"},
    VIDEOS = {"mp4", "webm", "mov", "avi"}
}

-- YouTube API settings
Config.YOUTUBE = {
    API_KEY = "YOUR_YOUTUBE_API_KEY", -- Should be set via environment variable in production
    BASE_URL = "https://www.googleapis.com/youtube/v3",
    VIDEO_INFO_ENDPOINT = "/videos",
    THUMBNAIL_QUALITY = "maxresdefault" -- maxresdefault, hqdefault, mqdefault, sddefault, default
}

-- Processing presets
Config.PRESETS = {
    DEFAULT = {
        maxDuration = 30, -- seconds
        frameRate = 1,    -- frames per second
        quality = 0.8,    -- 0.0 to 1.0
        generateThumbnails = true
    },
    HIGH_QUALITY = {
        maxDuration = 30,
        frameRate = 2,
        quality = 1.0,
        generateThumbnails = true
    },
    FAST = {
        maxDuration = 15,
        frameRate = 0.5,
        quality = 0.6,
        generateThumbnails = false
    }
}

-- Model generation defaults
Config.MODEL = {
    STYLES = {
        "standard",
        "voxel",
        "low_poly"
    },
    DEFAULT_STYLE = "standard",
    DEFAULT_SCALE = 1.0,
    MAX_TRIANGLES = 10000,
    LOD_LEVELS = {
        { distance = 50,  quality = 1.0 },
        { distance = 100, quality = 0.7 },
        { distance = 200, quality = 0.4 }
    }
}

-- Asset types
Config.ASSET_TYPES = {
    IMAGE = "image",
    VIDEO = "video",
    YOUTUBE = "youtube",
    TEXT = "text"
}

-- Error messages
Config.ERRORS = {
    INVALID_URL = "Invalid or unsupported URL",
    INVALID_FILE = "Invalid or unsupported file",
    DOWNLOAD_FAILED = "Failed to download asset",
    PROCESSING_FAILED = "Failed to process asset",
    API_ERROR = "API request failed"
}

-- Cache settings (in seconds)
Config.CACHE = {
    ENABLED = true,
    TTL = 3600, -- 1 hour
    MAX_ITEMS = 100
}

-- Logging
Config.LOGGING = {
    LEVEL = "info", -- debug, info, warn, error
    MAX_ENTRIES = 1000
}

return Config
