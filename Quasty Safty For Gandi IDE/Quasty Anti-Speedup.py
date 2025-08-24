"""
Anti-Speedup System for Scratch GANDI IDE
This system detects and prevents speed hacking/cheating in Scratch projects

@block.name: 🐼 Anti-Speedup
@block.desc: Detect and prevent speed hacking/cheating attempts

Features:
1. Initialize system with customizable FPS thresholds
2. Track frame times and calculate FPS
3. Detect abnormal frame rates (too high or too low)
4. Gradual suspicion level system
5. Cooldown mechanism to prevent false positives

Usage:
1. Call init_anti_speedup() at project start
2. Call update_frame_time() every frame
3. Periodically check check_speedup() or is_cheating_detected()

Documentation: https://dev.ccw.site/blog/posts/python-in-gandi-demo
"""

import time
import math

# System state variables
_last_frame_time = 0  # Timestamp of last frame
_frame_times = []     # Circular buffer of recent frame times
_suspicion_level = 0  # Current suspicion level (0-10)
_is_initialized = False  # Whether system is initialized
_min_fps = 10         # Minimum reasonable FPS
_max_fps = 120        # Maximum reasonable FPS
_max_suspicion = 10   # Threshold for cheating detection
_cooldown = 0         # Cooldown counter

def init_anti_speedup(min_fps=10, max_fps=120):
    """
    Initialize the anti-speedup detection system
    
    Args:
        min_fps (int): Minimum acceptable FPS (default: 10)
        max_fps (int): Maximum acceptable FPS (default: 120)
    
    Returns:
        str: Initialization status message
    """
    global _last_frame_time, _frame_times, _suspicion_level
    global _is_initialized, _min_fps, _max_fps, _cooldown
    
    # Validate input parameters
    if min_fps <= 0 or max_fps <= 0:
        return "Error: FPS values must be positive"
    if min_fps >= max_fps:
        return "Error: min_fps must be less than max_fps"
    
    _last_frame_time = time.time()
    _frame_times = []
    _suspicion_level = 0
    _is_initialized = True
    _min_fps = min_fps
    _max_fps = max_fps
    _cooldown = 0
    
    return "Anti-speedup system initialized successfully"

def update_frame_time():
    """
    Update frame timing information (call every frame)
    
    Returns:
        str: Status message or error if not initialized
    """
    global _last_frame_time, _frame_times, _cooldown
    
    if not _is_initialized:
        return "Error: System not initialized. Call init_anti_speedup() first"
    
    current_time = time.time()
    frame_time = current_time - _last_frame_time
    _last_frame_time = current_time
    
    # Add to frame time buffer (keep last 30 frames)
    _frame_times.append(frame_time)
    if len(_frame_times) > 30:
        _frame_times.pop(0)
    
    # Decrement cooldown counter
    if _cooldown > 0:
        _cooldown -= 1
    
    return "Frame time updated"

def check_speedup():
    """
    Check for speed hacking/cheating attempts
    
    Returns:
        tuple: (status_message, suspicion_level)
    """
    global _suspicion_level, _cooldown
    
    if not _is_initialized:
        return ("System not initialized", 0)
    
    if len(_frame_times) < 5:
        return ("Insufficient data (need at least 5 frames)", 0)
    
    if _cooldown > 0:
        return (f"Cooldown active ({_cooldown} frames remaining)", _suspicion_level)
    
    # Calculate average frame time and FPS
    avg_frame_time = sum(_frame_times) / len(_frame_times)
    current_fps = 1 / avg_frame_time if avg_frame_time > 0 else float('inf')
    
    # Check for abnormal FPS
    if current_fps < _min_fps:
        _suspicion_level += 1
        return (f"Abnormally low FPS detected ({current_fps:.1f} FPS)", _suspicion_level)
    elif current_fps > _max_fps:
        _suspicion_level += 2
        return (f"Abnormally high FPS detected ({current_fps:.1f} FPS)", _suspicion_level)
    else:
        # Normal FPS range - gradually reduce suspicion
        _suspicion_level = max(0, _suspicion_level - 0.2)
        return ("Normal operation", _suspicion_level)

def reset_suspicion():
    """
    Reset the suspicion level and activate cooldown
    
    Returns:
        str: Status message
    """
    global _suspicion_level, _cooldown
    
    _suspicion_level = 0
    _cooldown = 30  # 30-frame cooldown period
    return "Suspicion level reset and cooldown activated"

def get_suspicion_level():
    """
    Get current suspicion level (0-10)
    
    Returns:
        int: Current suspicion level (clamped to 0-10)
    """
    return min(_max_suspicion, max(0, math.floor(_suspicion_level)))

def is_cheating_detected():
    """
    Check if cheating has been definitively detected
    
    Returns:
        bool: True if cheating detected, False otherwise
    """
    return get_suspicion_level() >= _max_suspicion

# Functions exposed to Scratch
__all__ = [
    'init_anti_speedup',
    'update_frame_time',
    'check_speedup',
    'reset_suspicion',
    'get_suspicion_level',
    'is_cheating_detected'
]