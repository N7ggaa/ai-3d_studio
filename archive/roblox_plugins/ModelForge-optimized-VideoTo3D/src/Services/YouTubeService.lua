-- YouTubeService: Handles YouTube API integration

local HttpService = game:GetService("HttpService")
local Config = require(script.Parent.Parent.Config.YouTube)
local Logger = require(script.Parent.Parent.Utils.Logger)

local YouTubeService = {}
YouTubeService.__index = YouTubeService

function YouTubeService.new(apiKey)
    local self = setmetatable({}, YouTubeService)
    self.apiKey = apiKey or Config.API_KEY
    self.baseUrl = Config.BASE_URL
    self.logger = Logger.new("YouTubeService")
    return self
end

-- Get video info from YouTube API
function YouTubeService:getVideoInfo(videoId)
    local url = string.format(
        "%s/videos?id=%s&part=snippet,contentDetails,statistics&key=%s",
        self.baseUrl,
        videoId,
        self.apiKey
    )
    
    local success, response = pcall(function()
        return HttpService:JSONDecode(HttpService:GetAsync(url))
    end)
    
    if not success or not response.items or #response.items == 0 then
        self.logger:error("Failed to fetch video info:", response and response.error or "Unknown error")
        return nil
    end
    
    local video = response.items[1]
    return {
        id = video.id,
        title = video.snippet.title,
        description = video.snippet.description,
        thumbnail = video.snippet.thumbnails.high.url,
        duration = self:parseDuration(video.contentDetails.duration),
        width = video.snippet.thumbnails.high.width,
        height = video.snippet.thumbnails.high.height,
        viewCount = tonumber(video.statistics.viewCount),
        likeCount = tonumber(video.statistics.likeCount)
    }
end

-- Parse ISO 8601 duration format to seconds
function YouTubeService:parseDuration(duration)
    local patterns = {
        { "(%d+)D", 86400 },
        { "(%d+)H", 3600 },
        { "(%d+)M", 60 },
        { "(%d+)S", 1 }
    }
    
    local seconds = 0
    for _, pattern in ipairs(patterns) do
        local value = duration:match("PT[^"]*" .. pattern[1])
        if value then
            seconds = seconds + tonumber(value) * pattern[2]
        end
    end
    
    return seconds
end

-- Get YouTube video ID from URL
function YouTubeService:getVideoId(url)
    return url:match("^.*(?:youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=)([^#&?]*).*$")
end

-- Get video frames (placeholder - would use frame extraction service)
function YouTubeService:getVideoFrames(videoId, options)
    options = options or {}
    local frames = {}
    local frameCount = math.min(options.frameCount or 10, 30) -- Max 30 frames
    
    for i = 1, frameCount do
        table.insert(frames, {
            image = string.format("https://img.youtube.com/vi/%s/mqdefault.jpg", videoId),
            timestamp = i * (options.duration or 30) / frameCount,
            isKeyframe = i == 1 or i % 5 == 0
        })
    end
    
    return frames
end

return YouTubeService
