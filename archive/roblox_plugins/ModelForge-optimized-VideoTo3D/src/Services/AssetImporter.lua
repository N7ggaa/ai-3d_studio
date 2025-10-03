-- AssetImporter Service
-- Handles importing and processing of various asset types (videos, images, text)

local HttpService = game:GetService("HttpService")
local ContentProvider = game:GetService("ContentProvider")
local RunService = game:GetService("RunService")
local Path = require(script.Parent.Parent.Utils.Path)

local Config = require(script.Parent.Parent.Config.AssetImporter)
local FFmpegConfig = require(script.Parent.Parent.Config.FFmpeg)
local Logger = require(script.Parent.Parent.Utils.Logger)
local Utils = require(script.Parent.Parent.Utils.Utils)
local YouTubeService = require(script.Parent.YouTubeService)
local FFmpegService = require(script.Parent.FFmpegService)

local AssetImporter = {}
AssetImporter.__index = AssetImporter

-- Constants
local YOUTUBE_REGEX = "^%s*(?:https?://)?(?:www%.|m\.)?(?:youtu\.be/|youtube%.com/(?:embed/|v/|shorts/|watch\?v=|watch\?.+&v=))([%w_-]+).*$"
local IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "bmp"}
local VIDEO_EXTENSIONS = {"mp4", "webm", "mov", "avi"}

-- Create a new AssetImporter instance
function AssetImporter.new(apiKey, options)
    local self = setmetatable({}, AssetImporter)
    self.logger = Logger.new("AssetImporter")
    self.cache = {}
    self.options = options or {}
    
    -- Initialize services
    self.youTubeService = YouTubeService.new(apiKey)
    self.ffmpeg = FFmpegService.new(self.options.ffmpegPath)
    
    -- Check FFmpeg availability
    local ffmpegAvailable, ffmpegError = self.ffmpeg:isAvailable()
    if not ffmpegAvailable then
        self.logger:warn("FFmpeg not available: " .. tostring(ffmpegError))
    end
    
    -- Create temp directory if it doesn't exist
    self.tempDir = self.options.tempDir or (Path.getTempDir() .. "/VideoTo3D")
    if not Path.exists(self.tempDir) then
        Path.mkdir(self.tempDir, true)
    end
    
    return self
end

-- Check if a URL is a YouTube URL
function AssetImporter:isYouTubeUrl(url)
    return url:match(YOUTUBE_REGEX) ~= nil
end

-- Extract YouTube video ID from URL
function AssetImporter:getYouTubeId(url)
    return url:match(YOUTUBE_REGEX)
end

-- Check if a URL points to an image
function AssetImporter:isImageUrl(url)
    local extension = url:match("%.([^%.]+)$"):lower()
    return table.find(IMAGE_EXTENSIONS, extension) ~= nil
end

-- Check if a URL points to a video
function AssetImporter:isVideoUrl(url)
    local extension = url:match("%.([^%.]+)$"):lower()
    return table.find(VIDEO_EXTENSIONS, extension) ~= nil
end

-- Process a YouTube URL
function AssetImporter:processYouTubeUrl(url, options)
    local videoId = self.youTubeService:getVideoId(url)
    if not videoId then
        return {
            success = false,
            error = Config.ERRORS.INVALID_YOUTUBE_URL
        }
    end
    
    -- Get video info from YouTube API
    local videoInfo = self.youTubeService:getVideoInfo(videoId)
    if not videoInfo then
        return {
            success = false,
            error = Config.ERRORS.YOUTUBE_API_ERROR
        }
    end
    
    -- Get video frames
    local frames = self.youTubeService:getVideoFrames(videoId, {
        frameCount = math.min(options.frameRate or 1, 2) * (options.maxDuration or 30), -- Max 2 FPS for YouTube
        duration = videoInfo.duration
    })
    
    return {
        success = true,
        type = Config.ASSET_TYPES.YOUTUBE,
        videoId = videoId,
        title = videoInfo.title,
        description = videoInfo.description,
        thumbnail = videoInfo.thumbnail,
        duration = videoInfo.duration,
        width = videoInfo.width,
        height = videoInfo.height,
        viewCount = videoInfo.viewCount,
        likeCount = videoInfo.likeCount,
        frames = frames,
        metadata = {
            source = "youtube",
            videoId = videoId,
            originalUrl = url
        }
    }
end

-- Process an image URL or local file
function AssetImporter:processImageUrl(url, options)
    options = options or {}
    local isLocal = url:match("^[A-Za-z]:\\.*") or url:match("^/.*")
    
    -- For local files, use FFmpeg to process the image
    if isLocal then
        if not Path.exists(url) then
            return {
                success = false,
                error = "File not found: " .. url
            }
        end
        
        -- Create output path in temp directory
        local filename = Path.getFilename(url)
        local outputPath = Path.join(self.tempDir, "processed_" .. filename)
        
        -- Process image with FFmpeg
        local success, result = pcall(function()
            return self.ffmpeg:processImage(url, outputPath, {
                width = options.width or FFmpegConfig.DEFAULTS.IMAGE.MAX_WIDTH,
                height = options.height or FFmpegConfig.DEFAULTS.IMAGE.MAX_HEIGHT,
                quality = options.quality or FFmpegConfig.DEFAULTS.IMAGE.QUALITY
            })
        end)
        
        if not success or not result then
            return {
                success = false,
                error = "Failed to process image: " .. tostring(result)
            }
        end
        
        -- Get image dimensions (simplified for this example)
        local width, height = 1024, 1024 -- In a real implementation, use an image processing library
        
        return {
            success = true,
            type = Config.ASSET_TYPES.IMAGE,
            path = outputPath,
            isLocal = true,
            width = width,
            height = height,
            format = Path.getExtension(url):sub(2):lower(),
            frames = {
                {
                    image = outputPath,
                    timestamp = 0,
                    isKeyframe = true
                }
            },
            metadata = {
                source = "local",
                originalPath = url,
                processedAt = os.time()
            }
        }
    else
        -- For remote images, return the URL (actual processing would happen on the server)
        return {
            success = true,
            type = Config.ASSET_TYPES.IMAGE,
            url = url,
            width = options.width or 1024,
            height = options.height or 1024,
            format = url:match("%.([^%.]+)$"),
            frames = {
                {
                    image = url,
                    timestamp = 0,
                    isKeyframe = true
                }
            },
            metadata = {
                source = "remote",
                originalUrl = url
            }
        }
    end
end

-- Process a local video file
function AssetImporter:processLocalFile(path, options)
    options = options or {}
    
    -- Validate file exists
    if not Path.exists(path) then
        return {
            success = false,
            error = "File not found: " .. path
        }
    end
    
    -- Get file extension and validate format
    local extension = Path.getExtension(path):sub(2):lower()
    local isVideo = table.find(FFmpegConfig.SUPPORTED_FORMATS.VIDEO, extension) ~= nil
    local isImage = table.find(FFmpegConfig.SUPPORTED_FORMATS.IMAGE, extension) ~= nil
    
    if not isVideo and not isImage then
        return {
            success = false,
            error = "Unsupported file format: " .. extension
        }
    end
    
    -- For images, use the image processing method
    if isImage then
        return self:processImageUrl(path, options)
    end
    
    -- For videos, use FFmpeg to extract frames
    local outputDir = Path.join(self.tempDir, "frames_" .. os.time())
    
    -- Get video info
    local videoInfo, err = self.ffmpeg:getVideoInfo(path)
    if not videoInfo then
        return {
            success = false,
            error = "Failed to get video info: " .. tostring(err)
        }
    end
    
    -- Calculate frame extraction parameters
    local maxDuration = math.min(options.maxDuration or FFmpegConfig.DEFAULTS.VIDEO.MAX_DURATION, videoInfo.duration)
    local frameRate = math.min(options.frameRate or FFmpegConfig.DEFAULTS.VIDEO.FRAME_RATE, FFmpegConfig.MAX_FRAME_RATE)
    
    -- Extract frames
    local frames, frameErr = self.ffmpeg:extractFrames(
        path,
        outputDir,
        {
            frameRate = frameRate,
            duration = maxDuration,
            width = options.width,
            height = options.height
        }
    )
    
    if not frames then
        return {
            success = false,
            error = "Failed to extract frames: " .. tostring(frameErr)
        }
    end
    
    -- Convert frames to the expected format
    local processedFrames = {}
    for i, frame in ipairs(frames) do
        table.insert(processedFrames, {
            image = frame.path,
            timestamp = frame.timestamp,
            isKeyframe = frame.isKeyframe,
            width = options.width or videoInfo.width,
            height = options.height or videoInfo.height
        })
    end
    
    return {
        success = true,
        type = Config.ASSET_TYPES.VIDEO,
        path = path,
        isLocal = true,
        width = videoInfo.width,
        height = videoInfo.height,
        duration = videoInfo.duration,
        format = extension,
        frames = processedFrames,
        metadata = {
            source = "local",
            originalPath = path,
            processedAt = os.time(),
            frameCount = #processedFrames,
            frameRate = frameRate
        }
    }
end

-- Process a text prompt
function AssetImporter:processTextPrompt(prompt, options)
    -- In a real implementation, this would use an AI model to generate an image
    -- For now, we'll return placeholder data
    return {
        success = true,
        type = "text",
        prompt = prompt,
        width = 1024,
        height = 1024,
        frames = {
            {
                image = "rbxassetid://6031075926",
                timestamp = 0,
                isKeyframe = true,
                prompt = prompt
            }
        }
    }
end

-- Main import function
function AssetImporter:import(asset, options)
    options = options or {}
    
    -- Check cache first
    local cacheKey = HttpService:JSONEncode({
        asset = asset,
        options = options
    })
    
    if self.cache[cacheKey] then
        self.logger:debug("Returning cached result for:", asset)
        return self.cache[cacheKey]
    end
    
    -- Process based on asset type
    local result
    
    if type(asset) == "string" then
        if self:isYouTubeUrl(asset) then
            result = self:processYouTubeUrl(asset, options)
        elseif self:isImageUrl(asset) then
            result = self:processImageUrl(asset, options)
        elseif self:isVideoUrl(asset) then
            -- For now, treat other video URLs like YouTube
            result = self:processYouTubeUrl(asset, options)
        else
            -- Try to process as a local file path
            result = self:processLocalFile(asset, options)
        end
    elseif type(asset) == "table" and asset.type == "text" then
        result = self:processTextPrompt(asset.prompt, options)
    else
        result = {
            success = false,
            error = "Unsupported asset type"
        }
    end
    
    -- Cache the result
    if result.success then
        self.cache[cacheKey] = result
    end
    
    return result
end

-- Clean up resources
function AssetImporter:cleanup()
    self.cache = {}
    self.logger:info("Cleaned up resources")
end

return AssetImporter
