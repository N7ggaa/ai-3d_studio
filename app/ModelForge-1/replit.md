# Overview

This is an AI-powered 3D model generator that creates downloadable 3D models from text prompts and optional reference images. The application uses Point-E (OpenAI's point cloud diffusion model) to generate 3D point clouds, which are then converted to standard 3D formats like FBX and Blender files. Users can submit generation jobs through a web interface and track their progress.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
- **Template Engine**: Jinja2 templates with Bootstrap for responsive UI
- **Static Assets**: Custom CSS and JavaScript for enhanced user experience
- **User Interface**: Multi-page web application with generation form, job tracking, and download pages
- **File Upload**: Drag-and-drop functionality for reference images with client-side validation

## Backend Architecture
- **Web Framework**: Flask with SQLAlchemy for database operations
- **Database**: SQLite by default with PostgreSQL support via environment configuration
- **File Management**: Separate upload and generated file directories with configurable size limits
- **Job Processing**: Synchronous processing model with database status tracking
- **Error Handling**: Comprehensive logging and fallback mechanisms for model conversion

## AI/ML Pipeline
- **Primary Model**: Point-E (OpenAI's text-to-3D point cloud model) using the base40M-textvec configuration
- **Processing Flow**: Text prompt → Point cloud generation → Mesh conversion → Format export
- **Device Support**: CUDA GPU acceleration when available, CPU fallback
- **Model Loading**: Lazy initialization to reduce startup time

## Data Storage
- **Database Schema**: Single GenerationJob model tracking prompts, file paths, status, and timestamps
- **File Storage**: Local filesystem with organized upload/generated directories
- **Status Management**: Five-state job lifecycle (pending, processing, completed, failed)

## Export System
- **Primary Converter**: Trimesh library for OBJ to FBX conversion
- **Fallback System**: Blender automation for complex conversions
- **Supported Formats**: FBX and Blender (.blend) files for game engine compatibility
- **Format Strategy**: OBJ intermediate format for maximum compatibility

# External Dependencies

## AI/ML Libraries
- **Point-E**: OpenAI's point cloud diffusion model for text-to-3D generation
- **PyTorch**: Deep learning framework for model inference
- **Trimesh**: 3D mesh processing and format conversion

## Web Framework
- **Flask**: Python web framework with SQLAlchemy ORM
- **Bootstrap**: Frontend CSS framework for responsive design
- **Feather Icons**: Icon library for consistent UI elements

## File Processing
- **Pillow**: Image processing for reference image handling
- **Werkzeug**: File upload security and utilities
- **Optional Blender**: 3D software automation for advanced conversions

## Infrastructure
- **SQLite/PostgreSQL**: Database backend with environment-based configuration
- **ProxyFix**: WSGI middleware for deployment behind reverse proxies
- **Logging**: Python standard library for debugging and monitoring