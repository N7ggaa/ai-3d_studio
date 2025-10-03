-- HttpUtil: HTTP utility functions for the VideoTo3D plugin
-- Handles all HTTP requests with retries, timeouts, and error handling

local HttpService = game:GetService("HttpService")
local Logger = require(script.Parent.Logger)

local HttpUtil = {}
HttpUtil.__index = HttpUtil

-- Default configuration
local DEFAULT_CONFIG = {
    maxRetries = 3,
    timeout = 10, -- seconds
    retryDelay = 1, -- seconds
    userAgent = "VideoTo3D/1.0"
}

-- Create a new HttpUtil instance
function HttpUtil.new(config)
    local self = setmetatable({}, HttpUtil)
    
    -- Merge default config with provided config
    self.config = setmetatable(config or {}, { __index = DEFAULT_CONFIG })
    self.logger = Logger.new("HttpUtil")
    
    return self
end

-- Make an HTTP GET request with retries
-- @param url string: The URL to request
-- @param headers table: Optional request headers
-- @return table: Response data and metadata
function HttpUtil:get(url, headers)
    return self:request({
        Url = url,
        Method = "GET",
        Headers = headers or {}
    })
end

-- Make an HTTP POST request with retries
-- @param url string: The URL to request
-- @param data table: The data to send (will be JSON-encoded)
-- @param headers table: Optional request headers
-- @return table: Response data and metadata
function HttpUtil:post(url, data, headers)
    local request = {
        Url = url,
        Method = "POST",
        Headers = headers or {},
        Body = type(data) == "table" and HttpService:JSONEncode(data) or tostring(data)
    }
    
    -- Set content type if not provided
    if not request.Headers["Content-Type"] then
        request.Headers["Content-Type"] = "application/json"
    end
    
    return self:request(request)
end

-- Make an HTTP request with retries and error handling
-- @param request table: The request parameters
-- @return table: Response data and metadata
function HttpUtil:request(request)
    local retries = 0
    local lastError
    
    -- Set default values
    request.Headers = request.Headers or {}
    request.Headers["User-Agent"] = request.Headers["User-Agent"] or self.config.userAgent
    
    -- Ensure HttpService is enabled
    if not HttpService.HttpEnabled then
        return self:handleError("HttpService is not enabled. Please enable it in game settings.")
    end
    
    -- Make the request with retries
    while retries <= self.config.maxRetries do
        local success, response = pcall(function()
            return HttpService:RequestAsync({
                Url = request.Url,
                Method = request.Method,
                Headers = request.Headers,
                Body = request.Body,
                Timeout = self.config.timeout
            })
        end)
        
        -- Check if the request was successful
        if success and response.Success then
            -- Try to parse JSON if content type is JSON
            local data = response.Body
            if response.Headers["Content-Type"] and 
               string.find(string.lower(response.Headers["Content-Type"]), "application/json") then
                local success, result = pcall(function()
                    return HttpService:JSONDecode(data)
                end)
                if success then
                    data = result
                end
            end
            
            return {
                success = true,
                status = response.StatusCode,
                statusText = response.StatusMessage,
                headers = response.Headers,
                data = data,
                rawResponse = response
            }
        end
        
        -- Handle errors
        lastError = response or "Unknown error"
        retries = retries + 1
        
        -- Log the error
        self.logger:warn(string.format(
            "Request failed (attempt %d/%d): %s",
            retries,
            self.config.maxRetries + 1,
            tostring(lastError)
        ))
        
        -- Don't retry if we've reached max retries
        if retries > self.config.maxRetries then
            break
        end
        
        -- Wait before retrying
        task.wait(self.config.retryDelay)
    end
    
    -- All retries failed
    return self:handleError("Max retries reached", lastError)
end

-- Handle HTTP errors
function HttpUtil:handleError(message, errorDetails)
    local errorInfo = {
        success = false,
        error = message,
        details = errorDetails,
        timestamp = os.time()
    }
    
    self.logger:error("HTTP Error:", errorInfo)
    
    return errorInfo
end

-- Check if a URL is valid
function HttpUtil:isValidUrl(url)
    if not url or type(url) ~= "string" then
        return false
    end
    
    -- Simple URL validation
    return string.match(url, "^https?://[%w-_%.%?%.:/%+=&]+$") ~= nil
end

-- Extract domain from URL
function HttpUtil:getDomain(url)
    if not self:isValidUrl(url) then
        return nil
    end
    
    -- Extract domain using pattern matching
    local domain = string.match(url, "^https?://([^/]+)")
    return domain and string.lower(domain)
end

-- Check if URL is from a supported video platform
function HttpUtil:isSupportedVideoUrl(url)
    local domain = self:getDomain(url)
    if not domain then return false end
    
    local supportedDomains = {
        ["youtube.com"] = true,
        ["youtu.be"] = true,
        ["vimeo.com"] = true,
        ["dailymotion.com"] = true,
        ["twitch.tv"] = true
    }
    
    -- Check if domain or subdomain matches
    for supportedDomain in pairs(supportedDomains) do
        if domain == supportedDomain or string.find(domain, "%." .. supportedDomain .. "$") then
            return true
        end
    end
    
    return false
end

return HttpUtil
