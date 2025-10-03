-- test_video_to_3d_service.lua
-- Tests for the VideoTo3DService module

local TestService = game:GetService("TestService")
local HttpService = game:GetService("HttpService")

-- Load test utilities
local TestUtils = require(script.Parent.TestUtils)

-- Load the module to test
local VideoTo3DService = require(script.Parent.Parent.src.services.VideoTo3DService)

-- Create a test suite
local TestVideoTo3DService = {}
TestVideoTo3DService.__index = TestVideoTo3DService

function TestVideoTo3DService.new()
    local self = setmetatable({}, TestVideoTo3DService)
    
    -- Set up test environment
    self.testFolder = Instance.new("Folder")
    self.testFolder.Name = "TestVideoTo3DService"
    self.testFolder.Parent = TestService:FindFirstChild("TestResults") or workspace
    
    -- Create a test video (5 seconds, 30fps, 640x480)
    self.testVideoPath = self:_createTestVideo()
    
    -- Initialize the service
    self.service = VideoTo3DService.new({
        outputDir = "TestOutput/VideoModels",
        tempDir = "TestOutput/Temp",
        maxDuration = 2, -- Only process 2 seconds for testing
        targetFPS = 15,  -- Lower FPS for testing
        targetSize = {width = 320, height = 240}
    })
    
    return self
end

-- Create a simple test video
function TestVideoTo3DService:_createTestVideo()
    local videoPath = "TestOutput/test_video.mp4"
    
    -- In a real test, we would create a simple video file here
    -- For now, we'll just return a path to a non-existent file
    -- and mock the file operations in the tests
    return videoPath
end

-- Test video processing
function TestVideoTo3DService:testProcessVideo()
    -- Mock the file operations
    local mockFileOps = {
        isfile = function(path)
            return path == self.testVideoPath
        end,
        makefolder = function() end,
        listfiles = function(dir)
            if dir:find("frames") then
                return {
                    "frame_000001.jpg",
                    "frame_000002.jpg",
                    "frame_000003.jpg"
                }
            end
            return {}
        end
    }
    
    -- Mock the Python process
    local mockProcess = {
        read = function()
            return "Processing frame 1/30\nProcessing frame 2/30\n..."
        end,
        close = function()
            return true
        end
    }
    
    -- Mock the io.popen function
    local originalPopen = io.popen
    io.popen = function(cmd, mode)
        return mockProcess
    end
    
    -- Mock the Promise library
    local mockPromise = {
        new = function(func)
            return {
                andThen = function(self, callback)
                    callback({modelPath = "TestOutput/VideoModels/12345/model.rbxmx"})
                    return self
                end,
                catch = function(self, callback)
                    return self
                end
            }
        end
    }
    
    -- Replace the Promise global
    local originalPromise = _G.Promise
    _G.Promise = mockPromise
    
    -- Test the processVideo method
    local jobId, promise = self.service:processVideo(self.testVideoPath, {
        maxDuration = 2,
        targetFPS = 15
    })
    
    -- Verify the results
    assert(jobId ~= nil, "Job ID should not be nil")
    assert(type(jobId) == "string", "Job ID should be a string")
    assert(#jobId > 0, "Job ID should not be empty")
    
    -- Check the status
    local status = self.service:getStatus()
    assert(status.isProcessing == true, "Service should be processing")
    assert(status.currentJobId == jobId, "Current job ID should match")
    
    -- Clean up
    io.popen = originalPopen
    _G.Promise = originalPromise
    
    return true
end

-- Test canceling a job
function TestVideoTo3DService:testCancelJob()
    -- Start a job
    local jobId, promise = self.service:processVideo(self.testVideoPath)
    
    -- Cancel the job
    local result = self.service:cancelJob()
    
    -- Check the results
    assert(result == true, "cancelJob should return true when a job is running")
    
    local status = self.service:getStatus()
    assert(status.isProcessing == false, "Service should not be processing after cancel")
    assert(status.status == "cancelled", "Status should be 'cancelled'")
    
    return true
end

-- Test cleanup
function TestVideoTo3DService:testCleanup()
    -- Set up the test
    self.service.isProcessing = true
    self.service.currentJobId = "test123"
    self.service.progress = 0.5
    self.service.status = "processing"
    
    -- Mock the delfolder function
    local delfolderCalled = false
    local originalDelfolder = delfolder
    delfolder = function(path)
        delfolderCalled = true
    end
    
    -- Clean up
    self.service:cleanup(false)
    
    -- Check the results
    assert(delfolderCalled == true, "delfolder should be called when cleanup is called with keepOutput=false")
    assert(self.service.isProcessing == false, "isProcessing should be false after cleanup")
    assert(self.service.currentJobId == nil, "currentJobId should be nil after cleanup")
    assert(self.service.progress == 0, "progress should be 0 after cleanup")
    assert(self.service.status == "idle", "status should be 'idle' after cleanup")
    
    -- Restore the original function
    delfolder = originalDelfolder
    
    return true
end

-- Run all tests
function TestVideoTo3DService:runAllTests()
    local testResults = {}
    local passed = 0
    local failed = 0
    
    -- Run each test
    for name, test in pairs(TestVideoTo3DService) do
        if type(test) == "function" and name:find("^test") then
            print("\nRunning test:", name)
            
            local success, result = pcall(function()
                return test(self)
            end)
            
            if success and result then
                print("✅ Test passed:", name)
                passed = passed + 1
                testResults[name] = {status = "passed"}
            else
                print("❌ Test failed:", name)
                print("   Error:", result)
                failed = failed + 1
                testResults[name] = {
                    status = "failed",
                    error = tostring(result)
                }
            end
        end
    end
    
    -- Print summary
    print("\nTest Summary:")
    print(string.format("✅ %d tests passed", passed))
    print(string.format("❌ %d tests failed", failed))
    
    return {
        passed = passed,
        failed = failed,
        results = testResults
    }
end

-- Run tests when the script is executed
local testRunner = TestVideoTo3DService.new()
return testRunner:runAllTests()
