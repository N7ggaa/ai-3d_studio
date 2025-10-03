-- Logger utility for consistent logging throughout the plugin

local Logger = {}
Logger.__index = Logger

-- Log levels
Logger.LEVELS = {
    DEBUG = 1,
    INFO = 2,
    WARN = 3,
    ERROR = 4,
    NONE = 5
}

-- Create a new logger instance
function Logger.new(name, level)
    local self = setmetatable({}, Logger)
    
    self.name = name or "Logger"
    self.level = level or Logger.LEVELS.INFO
    self.enabled = true
    
    return self
end

-- Set the log level
function Logger:setLevel(level)
    if type(level) == "string" then
        level = Logger.LEVELS[level:upper()] or Logger.LEVELS.INFO
    end
    self.level = level or Logger.LEVELS.INFO
end

-- Enable or disable logging
function Logger:setEnabled(enabled)
    self.enabled = enabled ~= false
end

-- Log a debug message
function Logger:debug(message, ...)
    self:_log(Logger.LEVELS.DEBUG, "DEBUG", message, ...)
end

-- Log an info message
function Logger:info(message, ...)
    self:_log(Logger.LEVELS.INFO, "INFO", message, ...)
end

-- Log a warning message
function Logger:warn(message, ...)
    self:_log(Logger.LEVELS.WARN, "WARN", message, ...)
end

-- Log an error message
function Logger:error(message, ...)
    self:_log(Logger.LEVELS.ERROR, "ERROR", message, ...)
end

-- Internal log function
function Logger:_log(level, levelName, message, ...)
    if not self.enabled or level < self.level then
        return
    end
    
    -- Format the message
    local formattedMessage = string.format("[%s] [%s] %s", os.date("%H:%M:%S"), levelName, tostring(message))
    
    -- Handle additional arguments
    if select('#', ...) > 0 then
        local args = {...}
        for i, arg in ipairs(args) do
            if type(arg) == "table" then
                args[i] = self:_tableToString(arg)
            end
        end
        formattedMessage = string.format("%s %s", formattedMessage, table.concat(args, " "))
    end
    
    -- Output the message
    if level == Logger.LEVELS.ERROR then
        warn(string.format("[%s] %s", self.name, formattedMessage))
    else
        print(string.format("[%s] %s", self.name, formattedMessage))
    end
end

-- Convert a table to a string for logging
function Logger:_tableToString(t, indent)
    if not indent then indent = 0 end
    local str = "{\n"
    for k, v in pairs(t) do
        if type(k) ~= "number" then k = '\"'..k..'\"' end
        for i = 1, indent + 2 do str = str .. " " end
        if type(v) == "table" then
            str = str .. '['..k.."] = " .. self:_tableToString(v, indent + 2) .. ",\n"
        else
            if type(v) == "string" then v = '\"'..v..'\"' end
            str = str .. '['..k.."] = " .. tostring(v) .. ",\n"
        end
    end
    for i = 1, indent do str = str .. " " end
    return str .. "}"
end

return Logger
