-- Utils.lua
-- General utility functions for the VideoTo3D plugin

local Utils = {}

-- Deep copies a table
function Utils.deepCopy(original)
    local copy
    if type(original) == 'table' then
        copy = {}
        for k, v in next, original, nil do
            copy[Utils.deepCopy(k)] = Utils.deepCopy(v)
        end
        setmetatable(copy, Utils.deepCopy(getmetatable(original)))
    else
        copy = original
    end
    return copy
end

-- Formats a file size in bytes to a human-readable string
function Utils.formatFileSize(bytes)
    if bytes < 1024 then
        return string.format("%d B", bytes)
    elseif bytes < 1024 * 1024 then
        return string.format("%.1f KB", bytes / 1024)
    else
        return string.format("%.1f MB", bytes / (1024 * 1024))
    end
end

-- Creates a debounced function
function Utils.debounce(func, wait)
    local lastTime = 0
    return function(...)
        local now = tick()
        if now - lastTime >= wait then
            lastTime = now
            return func(...)
        end
    end
end

-- Throttles a function
function Utils.throttle(func, limit)
    local lastTime = 0
    return function(...)
        local now = tick()
        if now - lastTime >= limit then
            lastTime = now
            return func(...)
        end
    end
end

-- Checks if a value is a valid number
function Utils.isNumber(value)
    return type(value) == "number" and value == value -- checks for NaN
end

-- Clamps a value between min and max
function Utils.clamp(value, min, max)
    return math.max(min, math.min(max, value))
end

-- Rounds a number to the nearest decimal places
function Utils.round(num, numDecimalPlaces)
    local mult = 10^(numDecimalPlaces or 0)
    return math.floor(num * mult + 0.5) / mult
end

-- Generates a random string
function Utils.randomString(length)
    local charset = {}
    for i = 48, 57 do table.insert(charset, string.char(i)) end -- 0-9
    for i = 65, 90 do table.insert(charset, string.char(i)) end -- A-Z
    for i = 97, 122 do table.insert(charset, string.char(i)) end -- a-z
    
    local result = ""
    for i = 1, length do
        result = result .. charset[math.random(1, #charset)]
    end
    return result
end

-- Checks if a file exists
function Utils.fileExists(path)
    local file = io.open(path, "r")
    if file then
        file:close()
        return true
    end
    return false
end

-- Creates a directory if it doesn't exist
function Utils.ensureDir(dirPath)
    -- This is a placeholder as file system operations are restricted in Roblox
    -- In a real implementation, you would use appropriate file system functions
    return true
end

-- Converts a table to a string for debugging
function Utils.tableToString(tbl, indent)
    if not indent then indent = 0 end
    local str = "{\n"
    for k, v in pairs(tbl) do
        local formatting = string.rep("  ", indent + 1)
        if type(k) == "number" then
            k = "["..k.."]"
        elseif type(k) == "string" then
            k = "\""..k.."\""
        end
        if type(v) == "table" then
            v = Utils.tableToString(v, indent + 1)
        elseif type(v) == "string" then
            v = "\""..v.."\""
        end
        str = str .. formatting .. k .. " = " .. tostring(v) .. ",\n"
    end
    return str .. string.rep("  ", indent) .. "}"
end

return Utils
