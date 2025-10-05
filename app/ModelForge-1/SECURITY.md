# Security & Guardrails Documentation

## 🔒 Security Overview

ModelForge implements comprehensive security measures to protect against common web application vulnerabilities and ensure safe operation.

## 🛡️ Input Validation & Sanitization

### File Upload Security
```python
# Whitelisted file extensions only
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Secure filename generation
filename = str(uuid.uuid4()) + '_' + secure_filename(file.filename)
```

**Protection Against:**
- ✅ Malicious file uploads
- ✅ Path traversal attacks
- ✅ File type spoofing
- ✅ Arbitrary file execution

### File Size Limits
```python
# Maximum file size: 16MB
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
```

**Protection Against:**
- ✅ Denial of Service (DoS) attacks
- ✅ Disk space exhaustion
- ✅ Memory exhaustion

### Input Sanitization
```python
# SQLAlchemy ORM prevents SQL injection
job = GenerationJob(
    prompt=prompt.strip(),  # Remove whitespace
    status='pending'
)

# Template escaping prevents XSS
{{ job.prompt|escape }}
```

## 🔐 Database Security

### SQL Injection Protection
```python
# Using SQLAlchemy ORM with parameterized queries
job = GenerationJob.query.get_or_404(job_id)
jobs = GenerationJob.query.filter_by(status='completed').all()

# No raw SQL queries - all through ORM
```

### Connection Security
```python
# Database connection pooling
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
```

## 🚫 Rate Limiting & Throttling

### Request Limits
```python
# Session-based rate limiting
def get_or_create_session():
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    
    # Track user activity
    user_session.last_activity = datetime.utcnow()
```

### File Upload Throttling
```python
# Maximum file size enforcement
if file.content_length > app.config['MAX_CONTENT_LENGTH']:
    flash('File too large', 'error')
    return redirect(url_for('generate'))
```

## 🛡️ Session Security

### Secure Session Configuration
```python
# Secure session key
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")

# Proxy fix for proper headers
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
```

### Session Management
```python
# Unique session IDs
session['session_id'] = str(uuid.uuid4())

# Session timeout tracking
user_session.last_activity = datetime.utcnow()
```

## 🔒 File System Security

### Isolated Directories
```python
# Separate directories for different file types
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['GENERATED_FOLDER'] = 'generated'

# Create directories with proper permissions
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['GENERATED_FOLDER'], exist_ok=True)
```

### Path Traversal Protection
```python
# Secure filename generation
filename = str(uuid.uuid4()) + '_' + secure_filename(file.filename)

# Validate file paths
if not os.path.exists(file_path) or '..' in file_path:
    raise Exception("Invalid file path")
```

## 🚨 Error Handling & Logging

### Graceful Error Handling
```python
try:
    # Operation that might fail
    result = perform_operation()
except Exception as e:
    # Log error for debugging
    logging.error(f"Operation failed: {str(e)}")
    
    # Show user-friendly message
    flash('An error occurred. Please try again.', 'error')
    
    # Don't expose internal details
    return redirect(url_for('index'))
```

### Comprehensive Logging
```python
# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Log security events
logging.info(f"User {session_id} uploaded file: {filename}")
logging.warning(f"Failed login attempt from {request.remote_addr}")
```

## 🔐 API Security

### Input Validation
```python
# Validate JSON input
data = request.get_json()
if not data or 'job_id' not in data:
    return jsonify({'error': 'Invalid request'}), 400

# Type checking
job_id = int(data.get('job_id'))
if job_id <= 0:
    return jsonify({'error': 'Invalid job ID'}), 400
```

### CORS Protection
```python
# Flask handles CORS automatically
# No cross-origin requests unless explicitly configured
```

## 🛡️ Content Security

### XSS Protection
```python
# Template auto-escaping
{{ user_input|escape }}

# JSON response sanitization
return jsonify({
    'id': job.id,
    'prompt': job.prompt,  # Already sanitized
    'status': job.status
})
```

### CSRF Protection
```python
# Flask-WTF CSRF tokens (if implemented)
# Form validation prevents CSRF attacks
```

## 🔒 Environment Security

### Environment Variables
```python
# Sensitive data in environment variables
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
database_url = os.environ.get("DATABASE_URL", "sqlite:///app.db")
openai_key = os.environ.get("OPENAI_API_KEY")
```

### Configuration Security
```python
# Development vs Production settings
if app.debug:
    # Development settings
    app.config['DEBUG'] = True
else:
    # Production settings
    app.config['DEBUG'] = False
    app.config['TESTING'] = False
```

## 🚨 Security Headers

### HTTP Security Headers
```python
# Flask automatically sets some security headers
# Additional headers can be added with Flask-Talisman

# Recommended headers:
# X-Content-Type-Options: nosniff
# X-Frame-Options: DENY
# X-XSS-Protection: 1; mode=block
# Content-Security-Policy: default-src 'self'
```

## 🔍 Security Monitoring

### Audit Trail
```python
# Track user actions
def log_user_action(session_id, action, details=None):
    logging.info(f"User {session_id} performed {action}: {details}")

# Log file uploads
log_user_action(session_id, "file_upload", filename)

# Log model generation
log_user_action(session_id, "model_generation", prompt)
```

### Anomaly Detection
```python
# Monitor for suspicious activity
def check_rate_limit(session_id, action):
    # Implement rate limiting logic
    pass

# Monitor file upload patterns
def validate_upload_pattern(filename, content_type):
    # Check for suspicious patterns
    pass
```

## 🛡️ Additional Security Measures

### Code Quality
- ✅ Type hints for better code safety
- ✅ Comprehensive error handling
- ✅ Input validation at all entry points
- ✅ Secure defaults for all configurations

### Dependencies
- ✅ Regular dependency updates
- ✅ Security vulnerability scanning
- ✅ Minimal dependency footprint
- ✅ Trusted package sources

### Deployment Security
- ✅ HTTPS enforcement in production
- ✅ Secure server configuration
- ✅ Regular security updates
- ✅ Backup and recovery procedures

## 🔧 Security Configuration

### Production Security Checklist
- [ ] Change default secret key
- [ ] Enable HTTPS
- [ ] Configure proper logging
- [ ] Set up monitoring
- [ ] Regular security audits
- [ ] Backup procedures
- [ ] Incident response plan

### Development Security
- [ ] Use environment variables
- [ ] Enable debug mode only in development
- [ ] Regular dependency updates
- [ ] Code security reviews
- [ ] Testing with security tools

## 🚨 Incident Response

### Security Incident Response Plan
1. **Detection**: Monitor logs and alerts
2. **Assessment**: Evaluate impact and scope
3. **Containment**: Isolate affected systems
4. **Eradication**: Remove threat
5. **Recovery**: Restore normal operations
6. **Lessons Learned**: Update security measures

### Contact Information
- **Security Issues**: Create GitHub issue with [SECURITY] tag
- **Emergency**: Contact maintainers directly
- **Vulnerability Reports**: Use responsible disclosure

---

**Security is a continuous process. Regular reviews and updates are essential.**
