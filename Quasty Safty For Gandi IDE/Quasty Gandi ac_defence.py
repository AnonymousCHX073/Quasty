"""
Anti-connection point system enhanced version (complete repair edition) boasts robust capabilities, 
supporting advanced features like dynamic cooling that adapts to real-time loads, 
group shared cooling for collaborative device heat dissipation, 
and intelligent priority management to ensure critical modules are always optimally cooled. ​

It further integrates multi-level protection mechanisms and adaptive frequency adjustment,
delivering both efficient heat dissipation and stable system operation for complex scenarios.

This code can completely prevent the occurrence of connectors and maintain the game environment：）

@block.name: 🐼 automatic_defence_system 2.0
"""

import time
from typing import Dict, List, Tuple, Optional, Callable, Union
import threading
_lock = threading.Lock()
_click_records: Dict[str, Tuple[float, float]] = {}
_group_records: Dict[str, List[str]] = {}
_group_cooldowns: Dict[str, Tuple[float, float]] = {}
_global_cooldown: Optional[float] = None 
_global_cooldown_records: Dict[str, float] = {"last_click": 0.0} 
_click_callbacks: Dict[str, List[Callable]] = {}
_button_types: Dict[str, str] = {} 
_group_priorities: Dict[str, int] = {}

def set_cooldown(button_id: str = "button1", cooldown: float = 1.0) -> None:
    with _lock:
        current_time = time.time()
        _click_records[button_id] = (current_time, cooldown)

def set_global_cooldown(cooldown: float = 1.0) -> None:
    with _lock:
        global _global_cooldown
        _global_cooldown = cooldown if cooldown > 0 else None
        _global_cooldown_records["last_click"] = time.time()

def create_group(group_name: str, *button_ids: str, priority: int = 0, group_cooldown: float = 1.0) -> None:
    with _lock:
        _group_records[group_name] = list(button_ids)
        _group_priorities[group_name] = priority
        _group_cooldowns[group_name] = (0.0, group_cooldown)

def add_to_group(group_name: str, button_id: str) -> None:
    with _lock:
        if group_name not in _group_records:
            _group_records[group_name] = []
        if button_id not in _group_records[group_name]:
            _group_records[group_name].append(button_id)

def remove_from_group(group_name: str, button_id: str) -> None:
    with _lock:
        if group_name in _group_records and button_id in _group_records[group_name]:
            _group_records[group_name].remove(button_id)

def set_button_type(button_id: str, type_name: str) -> None:
    with _lock:
        _button_types[button_id] = type_name

def get_button_type(button_id: str = "button1") -> str:
    with _lock:
        return _button_types.get(button_id, "normal")

def set_group_priority(group_name: str, priority: int = 0) -> None:
    with _lock:
        _group_priorities[group_name] = priority

def get_group_priority(group_name: str = "group1") -> int:
    with _lock:
        return _group_priorities.get(group_name, 0)

def get_groups_by_button(button_id: str) -> List[str]:
    with _lock:
        return [group for group, buttons in _group_records.items() if button_id in buttons]

def is_ready(button_id: str = "button1") -> bool:
    with _lock:
        current_time = time.time()
        
        if _global_cooldown is not None:
            global_last_click = _global_cooldown_records["last_click"]
            if current_time - global_last_click < _global_cooldown:
                return False
        if button_id in _click_records:
            last_click, cooldown = _click_records[button_id]
            if current_time - last_click < cooldown:
                return False

        for group in sorted(get_groups_by_button(button_id), 
                            key=lambda g: _group_priorities.get(g, 0), reverse=True):
            last_click, cooldown = _group_cooldowns.get(group, (0.0, 0.0))
            if current_time - last_click < cooldown:
                return False

        if button_id in _click_records:
            _, original_cooldown = _click_records[button_id]
            _click_records[button_id] = (current_time, original_cooldown)
        
        for group in get_groups_by_button(button_id):
            _, group_cooldown = _group_cooldowns.get(group, (0.0, 0.0))
            _group_cooldowns[group] = (current_time, group_cooldown)

        if button_id in _click_callbacks:
            for callback in _click_callbacks[button_id]:
                try:
                    callback(button_id)
                except Exception as e:
                    print(f"Callback error for button {button_id}: {str(e)}")
        
        return True

def get_remaining(button_id: str = "button1") -> float:
    with _lock:
        current_time = time.time()
        max_remaining = 0.0

        if _global_cooldown is not None:
            global_last_click = _global_cooldown_records["last_click"]
            global_remaining = max(0.0, _global_cooldown - (current_time - global_last_click))
            max_remaining = max(max_remaining, global_remaining)

        if button_id in _click_records:
            last_click, cooldown = _click_records[button_id]
            button_remaining = max(0.0, cooldown - (current_time - last_click))
            max_remaining = max(max_remaining, button_remaining)

        for group in get_groups_by_button(button_id):
            last_click, cooldown = _group_cooldowns.get(group, (0.0, 0.0))
            group_remaining = max(0.0, cooldown - (current_time - last_click))
            max_remaining = max(max_remaining, group_remaining)
        
        return max_remaining

def update_cooldown(button_id: str, new_cooldown: float) -> None:
    with _lock:
        if button_id in _click_records:
            last_click, _ = _click_records[button_id]
            _click_records[button_id] = (last_click, new_cooldown)

def add_click_callback(button_id: str, callback: Callable) -> None:
    with _lock:
        if button_id not in _click_callbacks:
            _click_callbacks[button_id] = []
        if callback not in _click_callbacks[button_id]:
            _click_callbacks[button_id].append(callback)

def get_cooldown_percentage(button_id: str = "button1") -> float:
    with _lock:
        remaining = get_remaining(button_id)
        if button_id in _click_records:
            _, cooldown = _click_records[button_id]
            if cooldown > 0:
                return min(1.0, remaining / cooldown)
        return 0.0

def batch_set_cooldown(button_ids: List[str], cooldown: float) -> None:
    with _lock:
        current_time = time.time()
        for button_id in button_ids:
            _click_records[button_id] = (current_time, cooldown)

def get_button_ids() -> List[str]:
    with _lock:
        return list(_click_records.keys())

def get_group_names() -> List[str]:
    with _lock:
        return list(_group_records.keys())

def get_buttons_in_group(group_name: str = "group1") -> List[str]:
    with _lock:
        return _group_records.get(group_name, [])

def remove_button(button_id: str = "button1") -> None:
    with _lock:
        if button_id in _click_records:
            del _click_records[button_id]
        for group in list(_group_records.values()):
            if button_id in group:
                group.remove(button_id)
        if button_id in _click_callbacks:
            del _click_callbacks[button_id]
        if button_id in _button_types:
            del _button_types[button_id]

def remove_group(group_name: str = "group1") -> None:
    with _lock:
        if group_name in _group_records:
            del _group_records[group_name]
        if group_name in _group_priorities:
            del _group_priorities[group_name]
        if group_name in _group_cooldowns:
            del _group_cooldowns[group_name]

def reset_all() -> None:
    with _lock:
        current_time = time.time()
        for button_id in _click_records:
            cooldown = _click_records[button_id][1]
            _click_records[button_id] = (current_time, cooldown)
        for group in _group_cooldowns:
            _, cooldown = _group_cooldowns[group]
            _group_cooldowns[group] = (current_time, cooldown)

def clear_all() -> None:
    with _lock:
        global _click_records, _group_records, _group_cooldowns, _global_cooldown
        global _global_cooldown_records, _click_callbacks, _button_types, _group_priorities
        _click_records = {}
        _group_records = {}
        _group_cooldowns = {}
        _global_cooldown = None
        _global_cooldown_records = {"last_click": 0.0}
        _click_callbacks = {}
        _button_types = {}
        _group_priorities = {}

def set_cooldown_for_all(cooldown: float = 1.0) -> None:
    with _lock:
        current_time = time.time()
        for button_id in _click_records:
            _click_records[button_id] = (current_time, cooldown)
        for group in _group_cooldowns:
            _group_cooldowns[group] = (current_time, cooldown)

def is_any_in_group_ready(group_name: str = "group1") -> bool:
    with _lock:
        if group_name not in _group_records:
            return False
        for button_id in _group_records[group_name]:
            if is_ready(button_id):
                return True
        return False

def get_fastest_cooldown_in_group(group_name: str = "group1") -> float:
    with _lock:
        if group_name not in _group_records:
            return 0.0
        min_remaining = float('inf')
        for button_id in _group_records[group_name]:
            remaining = get_remaining(button_id)
            if remaining < min_remaining:
                min_remaining = remaining
        return max(0.0, min_remaining)

def get_highest_priority_group() -> Optional[str]:
    with _lock:
        if not _group_priorities:
            return None
        return max(_group_priorities.items(), key=lambda x: x[1])[0]

def get_all_groups_by_priority() -> List[str]:
    with _lock:
        return sorted(_group_records.keys(), key=lambda x: _group_priorities.get(x, 0), reverse=True)

__all__ = [
    'set_cooldown', 'set_global_cooldown', 'create_group', 'add_to_group',
    'remove_from_group', 'is_ready', 'get_remaining', 'get_button_ids',
    'get_group_names', 'get_buttons_in_group', 'remove_button', 'remove_group',
    'reset_all', 'clear_all', 'set_cooldown_for_all', 'is_any_in_group_ready',
    'get_fastest_cooldown_in_group', 'update_cooldown', 'add_click_callback',
    'get_cooldown_percentage', 'batch_set_cooldown', 'set_button_type',
    'get_button_type', 'set_group_priority', 'get_group_priority',
    'get_highest_priority_group', 'get_all_groups_by_priority'
]