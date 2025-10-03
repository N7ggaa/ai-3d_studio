-- run_tests.lua
-- Main test runner for the AI 3D Model Generator

local TestService = game:GetService("TestService")

-- Create a test results folder
local testResults = Instance.new("Folder")
testResults.Name = "TestResults_" .. os.time()
testResults.Parent = TestService:FindFirstChild("TestResults") or workspace

-- Function to run a test module
local function runTestModule(moduleName, testResultsFolder)
    local success, result = pcall(function()
        local module = require(script.Parent[moduleName])
        if type(module) == "table" and module.runAllTests then
            return module.runAllTests()
        else
            return {passed = 0, failed = 1, error = "Invalid test module: " .. moduleName}
        end
    end)
    
    if not success then
        return {
            name = moduleName,
            success = false,
            error = result,
            passed = 0,
            failed = 1
        }
    end
    
    return result
end

-- Main test runner
local function runAllTests()
    print("\n🚀 Starting Test Suite for AI 3D Model Generator\n")
    
    local totalPassed = 0
    local totalFailed = 0
    local testModules = {
        "test_sprite_generation"
        -- Add more test modules here as they're created
    }
    
    -- Run each test module
    for _, moduleName in ipairs(testModules) do
        print(string.format("\n=== Running Test Module: %s ===\n", moduleName))
        
        local startTime = os.clock()
        local results = runTestModule(moduleName, testResults)
        local duration = os.clock() - startTime
        
        if results then
            totalPassed = totalPassed + (results.passed or 0)
            totalFailed = totalFailed + (results.failed or 0)
            
            -- Print module results
            print(string.format("\n=== %s Results ===", moduleName))
            print(string.format("✅ Passed: %d", results.passed or 0))
            print(string.format("❌ Failed: %d", results.failed or 0))
            print(string.format("⏱️  Duration: %.2f seconds", duration))
            
            if results.error then
                print("\nError:", results.error)
            end
        end
    end
    
    -- Print summary
    print("\n" .. string.rep("=", 40))
    print("TEST SUITE SUMMARY")
    print(string.rep("=", 40))
    print(string.format("✅ Total Passed: %d", totalPassed))
    print(string.format("❌ Total Failed: %d", totalFailed))
    print(string.rep("=", 40))
    
    if totalFailed > 0 then
        error(string.format("Test suite failed with %d test(s) failing", totalFailed))
    end
    
    return totalPassed, totalFailed
end

-- Run the tests
local success, passed, failed = pcall(function()
    return runAllTests()
end)

if not success then
    print("\n❌ Test runner encountered an error:")
    print(passed) -- This contains the error message if pcall fails
    passed, failed = 0, 1
end

-- Return test results
return passed or 0, failed or 1
