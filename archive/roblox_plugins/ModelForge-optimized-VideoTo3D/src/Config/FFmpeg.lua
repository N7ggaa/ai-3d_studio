-- FFmpeg Configuration

local Config = {}

-- Path to FFmpeg executable (will be auto-detected if not specified)
Config.FFMPEG_PATH = "ffmpeg"

-- Maximum frame rate for frame extraction
Config.MAX_FRAME_RATE = 2 -- frames per second

-- Default output settings
Config.DEFAULTS = {
    -- Video settings
    VIDEO = {
        WIDTH = 1024,
        HEIGHT = 1024,
        FRAME_RATE = 1, -- frames per second
        MAX_DURATION = 30, -- seconds
        QUALITY = 8, -- 2-31, lower is better quality
        PRESET = "medium" -- ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow
    },
    
    -- Image settings
    IMAGE = {
        MAX_WIDTH = 2048,
        MAX_HEIGHT = 2048,
        QUALITY = 8, -- 2-31, lower is better quality
        FORMAT = "png" -- png, jpg, webp
    }
}

-- Supported input formats
Config.SUPPORTED_FORMATS = {
    VIDEO = {"mp4", "webm", "mov", "avi", "mkv", "flv", "wmv"},
    IMAGE = {"png", "jpg", "jpeg", "webp", "bmp", "tga", "tif", "tiff"},
    AUDIO = {"mp3", "wav", "ogg", "m4a", "aac"}
}

-- Error messages
Config.ERRORS = {
    FFMPEG_NOT_FOUND = "FFmpeg not found. Please install FFmpeg and add it to your system PATH.",
    INVALID_INPUT = "Invalid input file or format not supported.",
    PROCESSING_FAILED = "Failed to process media file.",
    INVALID_DURATION = "Invalid duration specified.",
    INVALID_FRAME_RATE = "Invalid frame rate specified.",
    OUTPUT_DIR_ERROR = "Failed to create output directory.",
    FILE_NOT_FOUND = "Input file not found.",
    PERMISSION_DENIED = "Permission denied when accessing file or directory.",
    UNSUPPORTED_FORMAT = "Unsupported file format."
}

-- Video codec settings
Config.CODECS = {
    VIDEO = {
        H264 = "libx264",
        VP9 = "libvpx-vp9",
        PRORES = "prores_ks",
        DEFAULT = "libx264"
    },
    AUDIO = {
        AAC = "aac",
        OPUS = "libopus",
        VORBIS = "libvorbis",
        DEFAULT = "aac"
    },
    PIXEL_FORMAT = "yuv420p"
}

-- Preset configurations for different use cases
Config.PRESETS = {
    HIGH_QUALITY = {
        videoCodec = "libx264",
        crf = 18,
        preset = "slow",
        tune = "film",
        profile = "high",
        level = 4.1
    },
    BALANCED = {
        videoCodec = "libx264",
        crf = 23,
        preset = "medium",
        tune = "film",
        profile = "main",
        level = 4.0
    },
    OPTIMIZED = {
        videoCodec = "libx264",
        crf = 28,
        preset = "fast",
        tune = "stillimage",
        profile = "baseline",
        level = 3.1
    }
}

-- Function to get the best matching preset
function Config.getPreset(name)
    return Config.PRESETS[name:upper()] or Config.PRESETS.BALANCED
end

-- Function to check if a format is supported
function Config.isFormatSupported(format, mediaType)
    format = format:lower()
    local formats = Config.SUPPORTED_FORMATS[mediaType:upper()]
    if not formats then return false end
    
    for _, f in ipairs(formats) do
        if f == format then
            return true
        end
    end
    
    return false
end

return Config
