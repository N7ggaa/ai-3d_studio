-- FFmpegService: Handles video and audio processing using FFmpeg

local Config = require(script.Parent.Parent.Config.FFmpeg)
local Logger = require(script.Parent.Parent.Utils.Logger)
local Utils = require(script.Parent.Parent.Utils.Utils)

local FFmpegService = {}
FFmpegService.__index = FFmpegService

function FFmpeg.new(ffmpegPath)
    local self = setmetatable({}, FFmpegService)
    self.ffmpegPath = ffmpegPath or Config.FFMPEG_PATH
    self.logger = Logger.new("FFmpegService")
    return self
end

-- Check if FFmpeg is available
function FFmpegService:isAvailable()
    if not self.ffmpegPath then
        return false, "FFmpeg path not configured"
    end
    
    local success, result = pcall(function()
        return os.execute(string.format('"%s" -version', self.ffmpegPath))
    end)
    
    return success and result == 0, "FFmpeg not found or not executable"
end

-- Get video information
function FFmpegService:getVideoInfo(filePath)
    local cmd = string.format(
        '"%s" -v error -show_entries format=duration:stream=width,height,duration -of json "%s"',
        self.ffmpegPath,
        filePath
    )
    
    local success, result = pcall(function()
        local handle = io.popen(cmd)
        local output = handle:read("*a")
        handle:close()
        return output
    end)
    
    if not success then
        return nil, "Failed to get video info: " .. tostring(result)
    end
    
    local ok, data = pcall(function()
        return game:GetService("HttpService"):JSONDecode(result)
    end)
    
    if not ok or not data.format then
        return nil, "Failed to parse video info"
    end
    
    return {
        duration = tonumber(data.format.duration) or 0,
        width = data.streams and data.streams[1] and tonumber(data.streams[1].width) or 0,
        height = data.streams and data.streams[1] and tonumber(data.streams[1].height) or 0
    }
end

-- Extract frames from video
function FFmpegService:extractFrames(filePath, outputDir, options)
    options = options or {}
    
    -- Ensure output directory exists
    if not isDir(outputDir) then
        local success, err = pcall(function()
            return os.execute(string.format('mkdir "%s"', outputDir))
        end)
        if not success then
            return nil, "Failed to create output directory: " .. tostring(err)
        end
    end
    
    -- Calculate frame rate
    local fps = math.min(options.frameRate or 1, Config.MAX_FRAME_RATE)
    local duration = options.duration or 30
    local frameCount = math.floor(fps * duration)
    
    -- Build FFmpeg command
    local outputPattern = outputDir .. "/frame_%04d.png"
    local cmd = string.format(
        '"%s" -i "%s" -vf "fps=%s,scale=%d:%d:force_original_aspect_ratio=decrease" -vsync vfr -q:v 2 "%s"',
        self.ffmpegPath,
        filePath,
        fps,
        options.width or -1,
        options.height or -1,
        outputPattern
    )
    
    -- Execute FFmpeg
    local success, result = pcall(function()
        return os.execute(cmd)
    end)
    
    if not success or result ~= 0 then
        return nil, "Failed to extract frames: " .. tostring(result)
    end
    
    -- Get list of generated frames
    local frames = {}
    for i = 1, frameCount do
        local framePath = string.format("%s/frame_%04d.png", outputDir, i)
        if isFile(framePath) then
            table.insert(frames, {
                path = framePath,
                timestamp = (i - 1) * (1 / fps),
                isKeyframe = i == 1 or i % math.max(1, math.floor(fps)) == 0
            })
        end
    end
    
    return frames
end

-- Convert image to Roblox-compatible format
function FFmpegService:processImage(inputPath, outputPath, options)
    options = options or {}
    
    local cmd = string.format(
        '"%s" -i "%s" -vf "scale=%d:%d:force_original_aspect_ratio=decrease" -q:v 2 "%s"',
        self.ffmpegPath,
        inputPath,
        options.width or 1024,
        options.height or 1024,
        outputPath
    )
    
    local success, result = pcall(function()
        return os.execute(cmd)
    end)
    
    if not success or result ~= 0 then
        return nil, "Failed to process image: " .. tostring(result)
    end
    
    return outputPath
end

-- Helper function to check if path is a directory
local function isDir(path)
    local f = io.open(path, "r")
    if f then
        local _, _, code = f:read(1)
        f:close()
        return code == 21 -- Directory error code
    end
    return false
end

-- Helper function to check if path is a file
local function isFile(path)
    local f = io.open(path, "r")
    if f then
        f:close()
        return true
    end
    return false
end

return FFmpegService
