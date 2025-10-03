-- Path: Cross-platform path manipulation utilities

local Path = {}
Path._VERSION = "1.0.0"
Path._DESCRIPTION = "Cross-platform path manipulation utilities"
Path._URL = "https://github.com/yourusername/yourrepo"
Path._LICENSE = [[
    MIT License
    Copyright (c) 2023 Your Name
]]

-- Platform detection
Path.SEPARATOR = package.config:sub(1,1)
Path.IS_WINDOWS = Path.SEPARATOR == "\\"
Path.IS_UNIX = not Path.IS_WINDOWS

-- Join path components
function Path.join(...)
    local parts = {...}
    local result = table.concat(parts, Path.SEPARATOR)
    
    -- Normalize path separators
    if Path.IS_WINDOWS then
        result = result:gsub("/", "\\")
    else
        result = result:gsub("\\", "/")
    end
    
    -- Remove duplicate separators
    result = result:gsub(Path.SEPARATOR .. "+", Path.SEPARATOR)
    
    return result
end

-- Get the directory name from a path
function Path.getDir(path)
    local dir = path:match("(.*)[/\\].*$")
    return dir or "."
end

-- Get the file name from a path
function Path.getFilename(path)
    return path:match(".*[/\\](.+)$") or path
end

-- Get the file extension (without the dot)
function Path.getExtension(path)
    return path:match("%.([^%.\/\\]+)$") or ""
end

-- Get the file name without extension
function Path.getBasename(path)
    local filename = Path.getFilename(path)
    return filename:match("(.+)%..+$") or filename
end

-- Check if a path is absolute
function Path.isAbsolute(path)
    if Path.IS_WINDOWS then
        return path:match("^%a:[\\/]") ~= nil or path:match("^[\\/][\\/]") ~= nil
    else
        return path:sub(1, 1) == "/"
    end
end

-- Normalize a path (resolve . and ..)
function Path.normalize(path)
    if path == "" then return "." end
    
    local isAbsolutePath = Path.isAbsolute(path)
    local isDir = path:sub(-1) == Path.SEPARATOR or path:sub(-1) == "/"
    local parts = {}
    
    -- Split path into components
    for part in path:gmatch("[^/\\]+") do
        if part == "." then
            -- Skip .
        elseif part == ".." and #parts > 0 and parts[#parts] ~= ".." then
            -- Go up one directory
            table.remove(parts)
        else
            table.insert(parts, part)
        end
    end
    
    -- Rebuild the path
    local result = table.concat(parts, Path.SEPARATOR)
    
    -- Handle absolute paths
    if isAbsolutePath then
        if Path.IS_WINDOWS then
            -- Handle Windows drive letters and UNC paths
            if path:match("^\\\\") then
                result = "\\\\" .. result -- UNC path
            else
                result = path:sub(1, 2) .. Path.SEPARATOR .. result
            end
        else
            result = Path.SEPARATOR .. result
        end
    elseif #result == 0 then
        result = "."
    end
    
    -- Add trailing slash for directories if needed
    if isDir and result ~= "/" and result:sub(-1) ~= Path.SEPARATOR then
        result = result .. Path.SEPARATOR
    end
    
    return result
end

-- Check if a path exists
function Path.exists(path)
    local file = io.open(path, "r")
    if file then
        file:close()
        return true
    end
    return false
end

-- Check if a path is a directory
function Path.isDir(path)
    local ok, err, code = os.rename(path, path)
    if not ok then
        if code == 13 then
            -- Permission denied, but it exists
            return true
        end
        return false
    end
    return true
end

-- Get the system's temporary directory
function Path.getTempDir()
    if Path.IS_WINDOWS then
        return os.getenv("TEMP") or os.getenv("TMP") or "C:\\Windows\\Temp"
    else
        return os.getenv("TMPDIR") or "/tmp"
    end
end

-- Create a directory (including parent directories if needed)
function Path.mkdir(path, recursive)
    if Path.exists(path) then
        return true
    end
    
    if recursive then
        -- Create parent directories first
        local parent = Path.getDir(path)
        if not Path.exists(parent) then
            local success = Path.mkdir(parent, true)
            if not success then
                return false
            end
        end
    end
    
    -- Create the directory
    if Path.IS_WINDOWS then
        return os.execute(string.format('mkdir "%s"', path))
    else
        return os.execute(string.format('mkdir -p "%s"', path))
    end
end

-- Remove a file or directory
function Path.remove(path, recursive)
    if not Path.exists(path) then
        return true
    end
    
    if Path.IS_WINDOWS then
        if recursive then
            return os.execute(string.format('rmdir /s /q "%s"', path))
        else
            return os.execute(string.format('del /q "%s"', path))
        end
    else
        if recursive then
            return os.execute(string.format('rm -rf "%s"', path))
        else
            return os.execute(string.format('rm -f "%s"', path))
        end
    end
end

-- List files in a directory
function Path.listFiles(dir, pattern)
    local files = {}
    local cmd
    
    if Path.IS_WINDOWS then
        cmd = string.format('dir /b /a-d "%s"', dir)
    else
        cmd = string.format('ls -1 "%s"', dir)
    end
    
    local handle = io.popen(cmd)
    if handle then
        for file in handle:lines() do
            if not pattern or file:match(pattern) then
                table.insert(files, Path.join(dir, file))
            end
        end
        handle:close()
    end
    
    return files
end

-- List directories in a directory
function Path.listDirs(dir, pattern)
    local dirs = {}
    local cmd
    
    if Path.IS_WINDOWS then
        cmd = string.format('dir /b /ad "%s"', dir)
    else
        cmd = string.format('ls -d "%s"/*/', dir)
    end
    
    local handle = io.popen(cmd)
    if handle then
        for dirname in handle:lines() do
            if not pattern or dirname:match(pattern) then
                table.insert(dirs, dirname)
            end
        end
        handle:close()
    end
    
    return dirs
end

-- Get the file size in bytes
function Path.getSize(path)
    local file = io.open(path, "r")
    if not file then return 0 end
    local size = file:seek("end")
    file:close()
    return size
end

-- Get the file modification time
function Path.getMtime(path)
    if Path.IS_WINDOWS then
        -- Windows implementation would use os.execute with dir command
        -- This is a simplified version
        return os.time()
    else
        -- Unix implementation
        local handle = io.popen(string.format('stat -c %%Y "%s"', path))
        if handle then
            local result = handle:read("*n")
            handle:close()
            return result
        end
        return os.time()
    end
end

-- Copy a file
function Path.copy(src, dst)
    local srcFile = io.open(src, "rb")
    if not srcFile then return false end
    
    local dstFile = io.open(dst, "wb")
    if not dstFile then
        srcFile:close()
        return false
    end
    
    local data = srcFile:read("*a")
    dstFile:write(data)
    
    srcFile:close()
    dstFile:close()
    
    return true
end

-- Move a file or directory
function Path.move(src, dst)
    if Path.IS_WINDOWS then
        return os.execute(string.format('move /Y "%s" "%s"', src, dst)) == 0
    else
        return os.execute(string.format('mv -f "%s" "%s"', src, dst)) == 0
    end
end

-- Get the current working directory
function Path.cwd()
    if Path.IS_WINDOWS then
        return io.popen("cd"):read("*l") or "."
    else
        return io.popen("pwd"):read("*l") or "."
    end
end

-- Get the absolute path
function Path.abs(path)
    if Path.isAbsolute(path) then
        return Path.normalize(path)
    end
    return Path.normalize(Path.join(Path.cwd(), path))
end

-- Get the relative path from one path to another
function Path.relative(path, start)
    start = start or "."
    
    local function split(path)
        local parts = {}
        for part in path:gmatch("[^/\\]+") do
            table.insert(parts, part)
        end
        return parts
    end
    
    local startParts = split(Path.abs(start))
    local pathParts = split(Path.abs(path))
    
    -- Find the common prefix
    local i = 1
    while i <= #startParts and i <= #pathParts and startParts[i] == pathParts[i] do
        i = i + 1
    end
    
    -- Calculate the relative path
    local relParts = {}
    for j = i, #startParts do
        table.insert(relParts, "..")
    end
    
    for j = i, #pathParts do
        table.insert(relParts, pathParts[j])
    end
    
    if #relParts == 0 then
        return "."
    end
    
    return table.concat(relParts, Path.SEPARATOR)
end

return Path
