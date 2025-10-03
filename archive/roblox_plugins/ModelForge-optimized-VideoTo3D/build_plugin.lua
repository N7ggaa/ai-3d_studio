-- Build script for VideoTo3D plugin
-- Run this script in Roblox Studio to build the plugin

local HttpService = game:GetService("HttpService")
local PluginService = game:GetService("PluginManager")

local function build()
    -- Create a new plugin instance
    local plugin = Instance.new("Plugin")
    plugin.Name = "VideoTo3D"
    
    -- Create the main module
    local mainModule = Instance.new("ModuleScript")
    mainModule.Name = "Main"
    mainModule.Source = [[
        local Main = {}
        
        function Main.new(plugin)
            local self = setmetatable({}, {__index = Main})
            self.plugin = plugin
            self.isEnabled = false
            return self
        end
        
        function Main:Enable()
            if self.isEnabled then return end
            self.isEnabled = true
            
            -- Plugin enabled logic here
            print("VideoTo3D plugin enabled")
        end
        
        function Main:Disable()
            if not self.isEnabled then return end
            self.isEnabled = false
            
            -- Plugin disabled logic here
            print("VideoTo3D plugin disabled")
        end
        
        return Main
    ]]
    mainModule.Parent = plugin
    
    -- Create the main plugin script
    local mainScript = Instance.new("Script")
    mainScript.Name = "MainPlugin"
    mainScript.Source = [[
        local plugin = script.Parent
        local success, result = pcall(function()
            local Main = require(plugin.Main)
            local main = Main.new(plugin)
            
            -- Connect toolbar button
            local toolbar = plugin:CreateToolbar("VideoTo3D")
            local button = toolbar:CreateButton("VideoTo3D", "Convert video to 3D model", "rbxassetid://6031075926")
            
            local function toggle()
                if main.isEnabled then
                    main:Disable()
                    button:SetActive(false)
                else
                    main:Enable()
                    button:SetActive(true)
                end
            end
            
            button.Click:Connect(toggle)
            
            -- Clean up when plugin is unloaded
            plugin.Unloading:Connect(function()
                if main.isEnabled then
                    main:Disable()
                end
            end)
            
            return main
        end)
        
        if not success then
            warn("Failed to initialize VideoTo3D plugin:", result)
            error(result)
        end
    ]]
    mainScript.Parent = plugin
    
    -- Save the plugin
    local fileName = "VideoTo3D.rbxm"
    local success, message = pcall(function()
        plugin:Save("rbxm", fileName)
    end)
    
    if success then
        print("Successfully built plugin:", fileName)
    else
        warn("Failed to build plugin:", message)
    end
    
    return plugin
end

-- Run the build
return build()
