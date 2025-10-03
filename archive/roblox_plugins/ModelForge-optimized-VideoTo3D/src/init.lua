-- VideoTo3D Plugin
-- Main entry point

local Plugin = script:FindFirstAncestorWhichIsA("Plugin")
local Main = require(script.Parent.Main)

local function main()
    local success, result = pcall(function()
        return Main.new(Plugin)
    end)
    
    if not success then
        warn("Failed to initialize VideoTo3D plugin:", result)
        error(result)
    end
    
    return result
end

return main()
