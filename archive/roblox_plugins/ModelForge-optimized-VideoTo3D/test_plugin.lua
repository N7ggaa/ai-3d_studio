-- Test script for VideoTo3D plugin
-- Load this in Roblox Studio to test the plugin

local function testPlugin()
    print("=== Starting VideoTo3D Plugin Test ===")
    
    -- Test basic requirements
    print("Testing Roact...")
    local success, Roact = pcall(require, script.Parent.src.Vendor.Roact)
    if not success then
        warn("❌ Failed to load Roact:", Roact)
        return false
    end
    print("✅ Roact loaded successfully")
    
    print("Testing RoactRodux...")
    local success, RoactRodux = pcall(require, script.Parent.src.Vendor.RoactRodux)
    if not success then
        warn("❌ Failed to load RoactRodux:", RoactRodux)
        return false
    end
    print("✅ RoactRodux loaded successfully")
    
    print("Testing Flipper...")
    local success, Flipper = pcall(require, script.Parent.src.Vendor.Flipper)
    if not success then
        warn("❌ Failed to load Flipper:", Flipper)
        return false
    end
    print("✅ Flipper loaded successfully")
    
    -- Test main module
    print("\nTesting Main module...")
    local success, Main = pcall(require, script.Parent.src.Main)
    if not success then
        warn("❌ Failed to load Main module:", Main)
        return false
    end
    print("✅ Main module loaded successfully")
    
    -- Initialize the plugin
    print("\nInitializing plugin...")
    local success, result = pcall(function()
        local plugin = script.Parent
        return Main.new(plugin)
    end)
    
    if not success then
        warn("❌ Failed to initialize plugin:", result)
        return false
    end
    
    print("\n✅ VideoTo3D plugin loaded successfully!")
    return true
end

-- Run the test
local success, result = pcall(testPlugin)
if not success then
    warn("❌ Test failed with error:", result)
end

return success and result
