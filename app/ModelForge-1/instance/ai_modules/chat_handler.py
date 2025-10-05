import os
import logging
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import openai

# Set up OpenAI client if API key is available
openai_client = None
if os.environ.get("OPENAI_API_KEY"):
    openai_client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

class ChatHandler:
    """Handle AI chat conversations and command processing"""
    
    def __init__(self, db_session):
        self.db = db_session
        
    def process_message(self, message: str, session_id: str, project_id: Optional[int] = None) -> Dict:
        """
        Process a user message and generate AI response with actions
        
        Args:
            message: User's message
            session_id: Chat session identifier
            project_id: Optional project context
            
        Returns:
            Dictionary with response and any actions to take
        """
        try:
            # Store user message
            self.store_message(session_id, 'user', message, project_id=project_id)
            
            # Get conversation context
            context = self.get_conversation_context(session_id)
            
            # Process with AI
            if openai_client:
                response_data = self.process_with_ai(message, context, project_id)
            else:
                response_data = self.process_with_fallback(message, context, project_id)
            
            # Store AI response
            self.store_message(
                session_id, 
                'assistant', 
                response_data['response'], 
                meta_data=response_data.get('meta_data'),
                project_id=project_id
            )
            
            return response_data
            
        except Exception as e:
            logging.error(f"Error processing chat message: {e}")
            return {
                'response': "I'm having trouble processing your request right now. Please try again.",
                'actions': [],
                'error': str(e)
            }
    
    def process_with_ai(self, message: str, context: List[Dict], project_id: Optional[int] = None) -> Dict:
        """Process message using OpenAI API"""
        
        # Build system prompt
        system_prompt = self.build_system_prompt(project_id)
        
        # Build conversation messages
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add context messages
        for msg in context[-10:]:  # Keep last 10 messages for context
            messages.append({
                "role": msg['message_type'],
                "content": msg['content']
            })
        
        # Add current message
        messages.append({"role": "user", "content": message})
        
        try:
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = openai_client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                max_tokens=1500,
                temperature=0.7,
                functions=[
                    {
                        "name": "generate_3d_model",
                        "description": "Generate a 3D model from a text description",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "prompt": {"type": "string", "description": "Description of the 3D model"},
                                "project_id": {"type": "integer", "description": "Project ID to add model to"}
                            },
                            "required": ["prompt"]
                        }
                    },
                    {
                        "name": "generate_script",
                        "description": "Generate a script (Lua, Python, etc.) from description",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "prompt": {"type": "string", "description": "Description of script functionality"},
                                "script_type": {"type": "string", "description": "Type of script (lua, python, csharp)"},
                                "project_id": {"type": "integer", "description": "Project ID to add script to"}
                            },
                            "required": ["prompt", "script_type"]
                        }
                    },
                    {
                        "name": "create_project",
                        "description": "Create a new project",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string", "description": "Project name"},
                                "description": {"type": "string", "description": "Project description"},
                                "project_type": {"type": "string", "description": "Project type (roblox, unity, general)"}
                            },
                            "required": ["name", "description"]
                        }
                    },
                    {
                        "name": "generate_environment",
                        "description": "Generate a game environment/world",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "prompt": {"type": "string", "description": "Description of the environment"},
                                "project_id": {"type": "integer", "description": "Project ID to add environment to"}
                            },
                            "required": ["prompt"]
                        }
                    }
                ],
                function_call="auto"
            )
            
            response_message = response.choices[0].message
            
            # Check if AI wants to call a function
            if response_message.function_call:
                return self.handle_function_call(response_message.function_call, project_id)
            else:
                return {
                    'response': response_message.content,
                    'actions': [],
                    'meta_data': {'ai_generated': True}
                }
                
        except Exception as e:
            logging.error(f"OpenAI API error: {e}")
            return self.process_with_fallback(message, context, project_id)
    
    def process_with_fallback(self, message: str, context: List[Dict], project_id: Optional[int] = None) -> Dict:
        """Process message using rule-based fallback"""
        
        message_lower = message.lower()
        actions = []
        
        # Detect intent and generate response
        if any(keyword in message_lower for keyword in ['create', 'generate', 'make', 'build']):
            if any(keyword in message_lower for keyword in ['model', '3d', 'object', 'mesh']):
                # Extract model description
                prompt = self.extract_model_prompt(message)
                actions.append({
                    'type': 'generate_3d_model',
                    'params': {'prompt': prompt, 'project_id': project_id}
                })
                response = f"I'll generate a 3D model: {prompt}"
                
            elif any(keyword in message_lower for keyword in ['script', 'code', 'lua', 'python']):
                # Extract script description
                prompt = self.extract_script_prompt(message)
                script_type = self.detect_script_type(message)
                actions.append({
                    'type': 'generate_script',
                    'params': {'prompt': prompt, 'script_type': script_type, 'project_id': project_id}
                })
                response = f"I'll generate a {script_type} script: {prompt}"
                
            elif any(keyword in message_lower for keyword in ['project', 'game', 'world']):
                # Create new project
                name = self.extract_project_name(message)
                description = message
                project_type = self.detect_project_type(message)
                actions.append({
                    'type': 'create_project',
                    'params': {'name': name, 'description': description, 'project_type': project_type}
                })
                response = f"I'll create a new {project_type} project: {name}"
                
            elif any(keyword in message_lower for keyword in ['world', 'level', 'map', 'environment', 'scene']):
                # Generate environment
                prompt = message
                actions.append({
                    'type': 'generate_environment',
                    'params': {'prompt': prompt, 'project_id': project_id}
                })
                response = f"I'll generate an environment: {prompt}"
                
            else:
                response = "I can help you generate 3D models, scripts, environments, or create projects. What would you like to make?"
                
        elif any(keyword in message_lower for keyword in ['help', 'what can you do', 'commands']):
            response = self.get_help_response()
            
        elif any(keyword in message_lower for keyword in ['list', 'show', 'view']):
            if 'project' in message_lower:
                response = "Here are your projects: [Project list would be shown here]"
            elif 'model' in message_lower:
                response = "Here are your generated models: [Model list would be shown here]"
            else:
                response = "I can show you your projects, models, scripts, or environments. What would you like to see?"
                
        else:
            response = "I understand you want to work on something. Can you be more specific? I can help generate 3D models, scripts, environments, or manage projects."
        
        return {
            'response': response,
            'actions': actions,
            'meta_data': {'fallback_used': True, 'detected_intent': self.detect_intent(message)}
        }
    
    def handle_function_call(self, function_call, project_id: Optional[int] = None) -> Dict:
        """Handle OpenAI function calls"""
        
        function_name = function_call.name
        arguments = json.loads(function_call.arguments)
        
        # Add project_id if not provided but available from context
        if project_id and 'project_id' not in arguments:
            arguments['project_id'] = project_id
        
        actions = [{
            'type': function_name,
            'params': arguments
        }]
        
        # Generate appropriate response based on function
        if function_name == 'generate_3d_model':
            response = f"I'll generate a 3D model: {arguments['prompt']}"
        elif function_name == 'generate_script':
            response = f"I'll generate a {arguments['script_type']} script: {arguments['prompt']}"
        elif function_name == 'create_project':
            response = f"I'll create a new {arguments.get('project_type', 'general')} project: {arguments['name']}"
        elif function_name == 'generate_environment':
            response = f"I'll generate an environment: {arguments['prompt']}"
        else:
            response = f"I'll execute the {function_name} command for you."
        
        return {
            'response': response,
            'actions': actions,
            'meta_data': {'function_called': function_name, 'ai_generated': True}
        }
    
    def build_system_prompt(self, project_id: Optional[int] = None) -> str:
        """Build system prompt for AI"""
        
        base_prompt = """You are an AI assistant that helps users create game assets and manage game development projects. You can:

1. Generate 3D models from text descriptions
2. Create scripts (Lua for Roblox, Python, C#) 
3. Generate game environments and worlds
4. Create and manage projects
5. Provide guidance on game development

When users ask for something to be created or generated, use the appropriate function to take action. Be helpful, creative, and provide clear explanations of what you're doing.

For Roblox projects, focus on Lua scripting and Roblox-specific features.
For Unity projects, focus on C# scripting and Unity features.
For general projects, adapt to the user's needs.

Always be encouraging and help users learn game development concepts."""
        
        # Add project context if available
        if project_id:
            # In a real implementation, you'd fetch project details
            base_prompt += f"\n\nCurrent project context: Project ID {project_id}"
        
        return base_prompt
    
    def get_conversation_context(self, session_id: str, limit: int = 10) -> List[Dict]:
        """Get recent conversation context"""
        try:
            from models import ChatMessage
            messages = self.db.query(ChatMessage).filter_by(session_id=session_id)\
                .order_by(ChatMessage.created_at.desc()).limit(limit).all()
            
            return [msg.to_dict() for msg in reversed(messages)]
        except Exception as e:
            logging.error(f"Error getting conversation context: {e}")
            return []
    
    def store_message(self, session_id: str, message_type: str, content: str, 
                     meta_data: Optional[Dict] = None, project_id: Optional[int] = None):
        """Store message in database"""
        try:
            from models import ChatMessage
            message = ChatMessage(
                session_id=session_id,
                message_type=message_type,
                content=content,
                meta_data=meta_data,
                project_id=project_id
            )
            self.db.add(message)
            self.db.commit()
        except Exception as e:
            logging.error(f"Error storing message: {e}")
    
    def extract_model_prompt(self, message: str) -> str:
        """Extract 3D model description from message"""
        # Simple extraction - in production, use more sophisticated NLP
        keywords = ['create', 'generate', 'make', 'build', 'model', '3d', 'object']
        words = message.split()
        
        # Find where the description starts
        start_idx = 0
        for i, word in enumerate(words):
            if word.lower() in keywords:
                start_idx = i + 1
                break
        
        # Take everything after the action word
        if start_idx < len(words):
            return ' '.join(words[start_idx:])
        else:
            return message
    
    def extract_script_prompt(self, message: str) -> str:
        """Extract script description from message"""
        keywords = ['script', 'code', 'function', 'lua', 'python', 'create', 'generate', 'make']
        words = message.split()
        
        start_idx = 0
        for i, word in enumerate(words):
            if word.lower() in keywords:
                start_idx = i + 1
                break
        
        if start_idx < len(words):
            return ' '.join(words[start_idx:])
        else:
            return message
    
    def extract_project_name(self, message: str) -> str:
        """Extract project name from message"""
        words = message.split()
        
        # Look for patterns like "create project [name]" or "new game [name]"
        for i, word in enumerate(words):
            if word.lower() in ['project', 'game'] and i + 1 < len(words):
                # Take next few words as name
                name_words = []
                for j in range(i + 1, min(i + 4, len(words))):
                    if words[j].lower() not in ['that', 'which', 'with', 'using']:
                        name_words.append(words[j])
                    else:
                        break
                if name_words:
                    return ' '.join(name_words)
        
        # Fallback to generic name
        return f"New Project {datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def detect_script_type(self, message: str) -> str:
        """Detect script type from message"""
        message_lower = message.lower()
        
        if 'lua' in message_lower or 'roblox' in message_lower:
            return 'lua'
        elif 'python' in message_lower:
            return 'python'
        elif 'c#' in message_lower or 'csharp' in message_lower or 'unity' in message_lower:
            return 'csharp'
        else:
            return 'lua'  # Default to Lua for game scripting
    
    def detect_project_type(self, message: str) -> str:
        """Detect project type from message"""
        message_lower = message.lower()
        
        if 'roblox' in message_lower:
            return 'roblox'
        elif 'unity' in message_lower:
            return 'unity'
        elif 'unreal' in message_lower:
            return 'unreal'
        else:
            return 'general'
    
    def detect_intent(self, message: str) -> str:
        """Detect user intent from message"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['create', 'generate', 'make', 'build']):
            return 'create'
        elif any(word in message_lower for word in ['list', 'show', 'view', 'display']):
            return 'list'
        elif any(word in message_lower for word in ['help', 'how', 'what can you']):
            return 'help'
        elif any(word in message_lower for word in ['delete', 'remove', 'clear']):
            return 'delete'
        elif any(word in message_lower for word in ['edit', 'modify', 'change', 'update']):
            return 'edit'
        else:
            return 'unknown'
    
    def get_help_response(self) -> str:
        """Get help response"""
        return """I'm your AI game development assistant! Here's what I can help you with:

🎮 **Create Projects**: "Create a new Roblox RPG game" or "Start a Unity platformer project"

🎯 **Generate 3D Models**: "Create a medieval sword" or "Generate a futuristic spaceship"

💻 **Write Scripts**: "Create a Lua script for NPC dialogue" or "Generate Python code for inventory system"

🌍 **Build Environments**: "Create a fantasy forest world" or "Generate a space station map"

📋 **Manage Projects**: "List my projects" or "Show my models"

Just tell me what you want to create and I'll help you build it! You can be as specific or general as you like."""