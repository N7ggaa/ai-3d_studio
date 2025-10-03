-- VideoProcessor Service
-- Handles video input from various sources and frame extraction

local Config = require(script.Parent.Parent.Config)
local Logger = require(script.Parent.Logger)
local HttpUtil = require(script.Parent.HttpUtil)

local VideoProcessor = {}
VideoProcessor.__index = VideoProcessor

-- Video processing presets
local PROCESSING_PRESETS = {
    default = {
        frameRate = 1,          -- Frames per second
        maxDuration = 30,       -- Maximum duration in seconds
        quality = 0.8,          -- Quality (0-1)
        detectKeyframes = true,  -- Whether to detect keyframes
        audioEnabled = false    -- Whether to extract audio
    },
    high_quality = {
        frameRate = 2,
        maxDuration = 30,
        quality = 0.9,
        detectKeyframes = true,
        audioEnabled = false
    },
    fast = {
        frameRate = 0.5,
        maxDuration = 15,
        quality = 0.6,
        detectKeyframes = true,
        audioEnabled = false
    }
}

-- Initialize a new VideoProcessor
function VideoProcessor.new()
    local self = setmetatable({}, VideoProcessor)
    
    -- Initialize services
    self.httpService = game:GetService("HttpService")
    self.logger = Logger.new("VideoProcessor")
    
    -- Initialize caches
    self.frameCache = {}
    self.videoInfoCache = {}
    self.downloadQueue = {}
    self.isProcessing = false
    
    -- Initialize HTTP utility
    self.http = HttpUtil.new({
        maxRetries = 3,
        timeout = 30
    })
    
    return self
end

-- Process a video from a URL (YouTube, direct link, etc.)
-- @param url string: The URL of the video to process
-- @param options table: Processing options (optional)
-- @return table: Processed frames and metadata
function VideoProcessor:processFromUrl(url, options)
    self.logger:info("Processing video from URL:", url)
    
    -- Validate URL
    if not url or url == "" then
        return self.logger:error("No URL provided")
    end
    
    -- Check cache first
    if self.frameCache[url] then
        self.logger:debug("Using cached frames for URL:", url)
        return self.frameCache[url]
    end
    
    -- Merge options with defaults
    options = self:getProcessingOptions(options)
    
    -- Process based on URL type
    local result
    
    if self:isYoutubeUrl(url) then
        result = self:processYoutubeVideo(url, options)
    elseif self:isLocalFile(url) then
        result = self:processLocalFile(url, options)
    else
        result = self:processDirectVideo(url, options)
    end
    
    -- Cache the result
    if result and result.success then
        self.frameCache[url] = result
    end
    
    return result
end

-- Get processing options with defaults
function VideoProcessor:getProcessingOptions(customOptions)
    local options = {}
    
    -- Apply preset if specified
    if customOptions and customOptions.preset and PROCESSING_PRESETS[customOptions.preset] then
        for k, v in pairs(PROCESSING_PRESETS[customOptions.preset]) do
            options[k] = v
        end
    else
        -- Use default preset
        for k, v in pairs(PROCESSING_PRESETS.default) do
            options[k] = v
        end
    end
    
    -- Override with custom options
    if customOptions then
        for k, v in pairs(customOptions) do
            if v ~= nil and k ~= "preset" then
                options[k] = v
            end
        end
    end
    
    -- Ensure frame rate is within limits
    options.frameRate = math.max(0.1, math.min(10, options.frameRate or 1))
    options.maxDuration = math.max(1, math.min(300, options.maxDuration or 30))
    options.quality = math.max(0.1, math.min(1, options.quality or 0.8))
    
    return options
end

-- Check if a URL is a YouTube URL
function VideoProcessor:isYoutubeUrl(url)
    return string.find(string.lower(url), "youtube%.com") ~= nil or
           string.find(string.lower(url), "youtu%.be") ~= nil
end

-- Check if a path is a local file
function VideoProcessor:isLocalFile(path)
    -- In Roblox, we can't directly access the filesystem,
    -- but we can check for common file extensions
    local lowerPath = string.lower(path)
    return string.match(lowerPath, "%.mp4$") or
           string.match(lowerPath, "%.webm$") or
           string.match(lowerPath, "%.mov$") or
           string.match(lowerPath, "%.avi$")
end

-- Process a local video file
-- @param filePath string: Path to the local video file
-- @param options table: Processing options
-- @return table: Processed frames and metadata
function VideoProcessor:processLocalFile(filePath, options)
    self.logger:info("Processing local video file:", filePath)
    
    -- In a real implementation, this would:
    -- 1. Check file exists and is accessible
    -- 2. Use FFmpeg or similar to extract frames
    -- 3. Process frames according to options
    
    -- For now, return placeholder frames
    local frames = {}
    local frameCount = math.min(options.duration or 30, Config.VIDEO.MAX_DURATION)
    
    for i = 1, frameCount do
        table.insert(frames, {
            image = "rbxassetid://6031075926",  -- Placeholder
            timestamp = i / (options.frameRate or 1),
            isKeyframe = (i == 1 or i % 5 == 0)  -- Simulate keyframes
        })
    end
    
    return {
        success = true,
        frames = frames,
        metadata = {
            source = "local",
            duration = frameCount / (options.frameRate or 1),
            frameCount = frameCount,
            resolution = {width = 1280, height = 720}  -- Default resolution
        }
    }
end

-- Process a YouTube video
-- @param url string: YouTube video URL
-- @param options table: Processing options
-- @return table: Processed frames and metadata
function VideoProcessor:processYoutubeVideo(url, options)
    self.logger:info("Processing YouTube video:", url)
    
    -- Extract video ID from URL
    local videoId = self:extractYoutubeVideoId(url)
    if not videoId then
        return {
            success = false,
            error = "Invalid YouTube URL",
            details = "Could not extract video ID from URL"
        }
    end
    
    -- Check if we have cached info for this video
    if self.videoInfoCache[videoId] then
        self.logger:debug("Using cached video info for:", videoId)
        return self.videoInfoCache[videoId]
    end
    
    -- In a real implementation, this would:
    -- 1. Use YouTube Data API to get video info
    -- 2. Download the video or extract frames directly
    -- 3. Process frames according to options
    
    -- For now, return placeholder frames
    local frames = {}
    local frameCount = math.min(options.duration or 30, Config.VIDEO.MAX_DURATION)
    
    for i = 1, frameCount do
        table.insert(frames, {
            image = "rbxassetid://6031075926",  -- Placeholder
            timestamp = i / (options.frameRate or 1),
            isKeyframe = (i == 1 or i % 5 == 0)  -- Simulate keyframes
        })
    end
    
    local result = {
        success = true,
        frames = frames,
        metadata = {
            source = "youtube",
            videoId = videoId,
            duration = frameCount / (options.frameRate or 1),
            frameCount = frameCount,
            resolution = {width = 1280, height = 720}  -- Default resolution
        }
    }
    
    -- Cache the result
    self.videoInfoCache[videoId] = result
    
    return result
end

-- Extract YouTube video ID from URL
-- @param url string: YouTube URL
-- @return string|nil: Video ID or nil if not found
function VideoProcessor:extractYoutubeVideoId(url)
    if not url then return nil end
    
    -- Handle youtu.be/ID format
    local id = string.match(url, "youtu%.be/([%w-_]+)")
    if id then return id end
    
    -- Handle youtube.com/watch?v=ID format
    id = string.match(url, "[&?]v=([%w-_]+)")
    if id then return id end
    
    -- Handle youtube.com/embed/ID format
    id = string.match(url, "youtube%.com/embed/([%w-_]+)")
    if id then return id end
    
    -- Handle youtu.be/ID?t=123 format
    id = string.match(url, "youtu%.be/([%w-_]+)%?")
    if id then return id end
    
    -- Handle youtube.com/watch?feature=...&v=ID format
    id = string.match(url, "[&?]v=([%w-_]+)")
    
    return id
end

-- Process a direct video URL
-- @param url string: Direct video URL
-- @param options table: Processing options
-- @return table: Processed frames and metadata
function VideoProcessor:processDirectVideo(url, options)
    self.logger:info("Processing direct video URL:", url)
    
    -- In a real implementation, this would:
    -- 1. Download the video
    -- 2. Extract frames using FFmpeg
    -- 3. Process frames according to options
    
    -- For now, return placeholder frames
    local frames = {}
    local frameCount = math.min(options.duration or 30, Config.VIDEO.MAX_DURATION)
    
    for i = 1, frameCount do
        table.insert(frames, {
            image = "rbxassetid://6031075926",  -- Placeholder
            timestamp = i / (options.frameRate or 1),
            isKeyframe = (i == 1 or i % 5 == 0)  -- Simulate keyframes
        })
    end
    
    return {
        success = true,
        frames = frames,
        metadata = {
            source = "direct",
            url = url,
            duration = frameCount / (options.frameRate or 1),
            frameCount = frameCount,
            resolution = {width = 1280, height = 720}  -- Default resolution
        }
    }
end

-- Clean up resources
function VideoProcessor:cleanup()
    self.frameCache = {}
    self.videoInfoCache = {}
    self.downloadQueue = {}
    self.isProcessing = false
end

return VideoProcessor
