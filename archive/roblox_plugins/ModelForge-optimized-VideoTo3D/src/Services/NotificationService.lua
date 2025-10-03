-- NotificationService: Manages the display of notifications to the user

local Roact = require(script.Parent.Parent.Vendor.Roact)
local Flipper = require(script.Parent.Parent.Vendor.Flipper)

local Notification = require(script.Parent.Parent.Components.Notification)

local NotificationService = {}
NotificationService.__index = NotificationService

-- Create a new NotificationService
function NotificationService.new(store)
    local self = setmetatable({}, NotificationService)
    
    -- Store the Redux store
    self.store = store
    
    -- State
    self.notifications = {}
    self.nextId = 1
    
    -- Create a container for notifications
    self.container = Instance.new("ScreenGui")
    self.container.Name = "NotificationService"
    self.container.ResetOnSpawn = false
    self.container.ZIndexBehavior = Enum.ZIndexBehavior.Sibling
    self.container.Parent = game:GetService("CoreGui")
    
    -- Create a folder for notifications
    self.folder = Instance.new("Folder")
    self.folder.Name = "Notifications"
    self.folder.Parent = self.container
    
    return self
end

-- Generate a unique ID for a notification
function NotificationService:generateId()
    local id = self.nextId
    self.nextId = self.nextId + 1
    return id
end

-- Show a notification
function NotificationService:show(notificationProps)
    -- Generate a unique ID for the notification
    local id = tostring(self:generateId())
    
    -- Set default values
    notificationProps.Id = id
    notificationProps.Timestamp = os.time()
    
    -- Add to notifications list
    self.notifications[id] = notificationProps
    
    -- Create the notification component
    local notification = Roact.createElement(Notification, notificationProps)
    
    -- Mount the notification
    local handle = Roact.mount(notification, self.folder, id)
    
    -- Store the Roact handle for cleanup
    self.notifications[id]._handle = handle
    
    return id
end

-- Show an info notification
function NotificationService:info(message, options)
    options = options or {}
    options.Message = message
    options.Type = "info"
    options.Duration = options.Duration or 5
    
    return self:show(options)
end

-- Show a success notification
function NotificationService:success(message, options)
    options = options or {}
    options.Message = message
    options.Type = "success"
    options.Duration = options.Duration or 5
    
    return self:show(options)
end

-- Show a warning notification
function NotificationService:warning(message, options)
    options = options or {}
    options.Message = message
    options.Type = "warning"
    options.Duration = options.Duration or 5
    
    return self:show(options)
end

-- Show an error notification
function NotificationService:error(message, options)
    options = options or {}
    options.Message = message
    options.Type = "error"
    options.Duration = options.Duration or 10
    
    return self:show(options)
end

-- Dismiss a notification by ID
function NotificationService:dismiss(id)
    local notification = self.notifications[id]
    if not notification then return end
    
    -- Unmount the Roact component
    if notification._handle then
        Roact.unmount(notification._handle)
    end
    
    -- Remove from notifications list
    self.notifications[id] = nil
    
    -- Call the onDismiss callback if provided
    if notification.OnDismiss then
        notification.OnDismiss(id)
    end
end

-- Dismiss all notifications
function NotificationService:dismissAll()
    for id, _ in pairs(self.notifications) do
        self:dismiss(id)
    end
end

-- Update a notification
function NotificationService:update(id, updates)
    local notification = self.notifications[id]
    if not notification then return end
    
    -- Update the notification
    for key, value in pairs(updates) do
        notification[key] = value
    end
    
    -- Re-render the notification
    if notification._handle then
        Roact.update(notification._handle, Roact.createElement(Notification, notification))
    end
end

-- Get the number of active notifications
function NotificationService:count()
    local count = 0
    for _ in pairs(self.notifications) do
        count = count + 1
    end
    return count
end

-- Clean up the notification service
function NotificationService:destroy()
    -- Dismiss all notifications
    self:dismissAll()
    
    -- Clean up the container
    if self.container then
        self.container:Destroy()
        self.container = nil
    end
    
    -- Clear references
    self.notifications = {}
    self.store = nil
end

return NotificationService
