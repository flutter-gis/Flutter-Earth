#!/usr/bin/env python3
"""
Real-Time Collaboration System for Earth Engine Crawler
Advanced multi-user collaboration with live updates and conflict resolution
"""

import asyncio
import json
import time
import threading
import uuid
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import logging
import websockets
from websockets.server import serve
import aiohttp
import sqlite3
import hashlib

# WebSocket and real-time imports
try:
    import websockets
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

@dataclass
class UserSession:
    """User session information"""
    user_id: str
    username: str
    session_id: str
    connected_at: datetime
    last_activity: datetime
    permissions: List[str]
    current_task: Optional[str]
    status: str  # 'active', 'idle', 'away'

@dataclass
class CollaborationEvent:
    """Real-time collaboration event"""
    event_id: str
    event_type: str  # 'data_update', 'user_join', 'user_leave', 'task_assignment', 'conflict_resolution'
    user_id: str
    timestamp: datetime
    data: Dict[str, Any]
    priority: int  # 1-10, higher is more important

@dataclass
class TaskAssignment:
    """Task assignment for collaborative work"""
    task_id: str
    task_type: str  # 'crawling', 'validation', 'enhancement', 'analysis'
    assigned_to: str
    assigned_at: datetime
    deadline: Optional[datetime]
    status: str  # 'pending', 'in_progress', 'completed', 'failed'
    priority: int
    description: str
    progress: float  # 0.0 to 1.0

class RealTimeCollaboration:
    """Advanced real-time collaboration system"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # User management
        self.active_users: Dict[str, UserSession] = {}
        self.user_locks: Dict[str, threading.Lock] = {}
        
        # Event management
        self.event_queue: List[CollaborationEvent] = []
        self.event_handlers: Dict[str, List[Callable]] = {}
        
        # Task management
        self.task_queue: List[TaskAssignment] = []
        self.completed_tasks: List[TaskAssignment] = []
        
        # Data synchronization
        self.shared_data: Dict[str, Any] = {}
        self.data_versions: Dict[str, int] = {}
        self.conflict_resolution_queue: List[Dict[str, Any]] = []
        
        # WebSocket server
        self.websocket_server = None
        self.websocket_clients: Dict[str, Any] = {}
        
        # Database for persistence
        self.db_path = "collaboration.db"
        self._init_database()
        
        # Start background tasks
        self._start_background_tasks()
    
    def _init_database(self):
        """Initialize collaboration database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_sessions (
                user_id TEXT PRIMARY KEY,
                username TEXT,
                session_id TEXT,
                connected_at TEXT,
                last_activity TEXT,
                permissions TEXT,
                current_task TEXT,
                status TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS collaboration_events (
                event_id TEXT PRIMARY KEY,
                event_type TEXT,
                user_id TEXT,
                timestamp TEXT,
                data TEXT,
                priority INTEGER
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS task_assignments (
                task_id TEXT PRIMARY KEY,
                task_type TEXT,
                assigned_to TEXT,
                assigned_at TEXT,
                deadline TEXT,
                status TEXT,
                priority INTEGER,
                description TEXT,
                progress REAL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS shared_data (
                key TEXT PRIMARY KEY,
                value TEXT,
                version INTEGER,
                last_updated TEXT,
                updated_by TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _start_background_tasks(self):
        """Start background collaboration tasks"""
        # Event processing thread
        self.event_thread = threading.Thread(target=self._process_events, daemon=True)
        self.event_thread.start()
        
        # Conflict resolution thread
        self.conflict_thread = threading.Thread(target=self._resolve_conflicts, daemon=True)
        self.conflict_thread.start()
        
        # User activity monitoring thread
        self.activity_thread = threading.Thread(target=self._monitor_user_activity, daemon=True)
        self.activity_thread.start()
    
    async def start_websocket_server(self, host: str = "localhost", port: int = 8765):
        """Start WebSocket server for real-time communication"""
        if not WEBSOCKETS_AVAILABLE:
            self.logger.error("WebSockets not available")
            return
        
        async def handle_client(websocket, path):
            client_id = str(uuid.uuid4())
            self.websocket_clients[client_id] = websocket
            
            try:
                async for message in websocket:
                    await self._handle_websocket_message(client_id, message)
            except websockets.exceptions.ConnectionClosed:
                pass
            finally:
                if client_id in self.websocket_clients:
                    del self.websocket_clients[client_id]
        
        self.websocket_server = await serve(handle_client, host, port)
        self.logger.info(f"WebSocket server started on {host}:{port}")
    
    async def _handle_websocket_message(self, client_id: str, message: str):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(message)
            message_type = data.get('type')
            
            if message_type == 'user_join':
                await self._handle_user_join(client_id, data)
            elif message_type == 'user_leave':
                await self._handle_user_leave(client_id, data)
            elif message_type == 'data_update':
                await self._handle_data_update(client_id, data)
            elif message_type == 'task_update':
                await self._handle_task_update(client_id, data)
            elif message_type == 'conflict_resolution':
                await self._handle_conflict_resolution(client_id, data)
            elif message_type == 'chat_message':
                await self._handle_chat_message(client_id, data)
            
        except json.JSONDecodeError:
            self.logger.error(f"Invalid JSON message from client {client_id}")
        except Exception as e:
            self.logger.error(f"Error handling WebSocket message: {e}")
    
    async def _handle_user_join(self, client_id: str, data: Dict[str, Any]):
        """Handle user joining the collaboration"""
        user_id = data.get('user_id')
        username = data.get('username', 'Anonymous')
        
        user_session = UserSession(
            user_id=user_id,
            username=username,
            session_id=client_id,
            connected_at=datetime.now(),
            last_activity=datetime.now(),
            permissions=data.get('permissions', ['read', 'write']),
            current_task=None,
            status='active'
        )
        
        self.active_users[user_id] = user_session
        self.user_locks[user_id] = threading.Lock()
        
        # Broadcast user join event
        event = CollaborationEvent(
            event_id=str(uuid.uuid4()),
            event_type='user_join',
            user_id=user_id,
            timestamp=datetime.now(),
            data={'username': username, 'permissions': user_session.permissions},
            priority=5
        )
        
        await self._broadcast_event(event)
        self.logger.info(f"User {username} joined collaboration")
    
    async def _handle_user_leave(self, client_id: str, data: Dict[str, Any]):
        """Handle user leaving the collaboration"""
        user_id = data.get('user_id')
        
        if user_id in self.active_users:
            username = self.active_users[user_id].username
            del self.active_users[user_id]
            
            if user_id in self.user_locks:
                del self.user_locks[user_id]
            
            # Broadcast user leave event
            event = CollaborationEvent(
                event_id=str(uuid.uuid4()),
                event_type='user_leave',
                user_id=user_id,
                timestamp=datetime.now(),
                data={'username': username},
                priority=5
            )
            
            await self._broadcast_event(event)
            self.logger.info(f"User {username} left collaboration")
    
    async def _handle_data_update(self, client_id: str, data: Dict[str, Any]):
        """Handle data updates from users"""
        user_id = data.get('user_id')
        key = data.get('key')
        value = data.get('value')
        version = data.get('version', 0)
        
        # Check for conflicts
        if key in self.data_versions and self.data_versions[key] > version:
            # Conflict detected
            conflict = {
                'key': key,
                'current_version': self.data_versions[key],
                'current_value': self.shared_data.get(key),
                'proposed_version': version,
                'proposed_value': value,
                'user_id': user_id,
                'timestamp': datetime.now()
            }
            
            self.conflict_resolution_queue.append(conflict)
            await self._notify_conflict(conflict)
        else:
            # No conflict, update data
            self.shared_data[key] = value
            self.data_versions[key] = version + 1
            
            # Broadcast update
            event = CollaborationEvent(
                event_id=str(uuid.uuid4()),
                event_type='data_update',
                user_id=user_id,
                timestamp=datetime.now(),
                data={'key': key, 'value': value, 'version': self.data_versions[key]},
                priority=7
            )
            
            await self._broadcast_event(event)
    
    async def _handle_task_update(self, client_id: str, data: Dict[str, Any]):
        """Handle task updates from users"""
        user_id = data.get('user_id')
        task_id = data.get('task_id')
        status = data.get('status')
        progress = data.get('progress', 0.0)
        
        # Update task
        for task in self.task_queue:
            if task.task_id == task_id:
                task.status = status
                task.progress = progress
                break
        
        # Broadcast task update
        event = CollaborationEvent(
            event_id=str(uuid.uuid4()),
            event_type='task_update',
            user_id=user_id,
            timestamp=datetime.now(),
            data={'task_id': task_id, 'status': status, 'progress': progress},
            priority=6
        )
        
        await self._broadcast_event(event)
    
    async def _handle_conflict_resolution(self, client_id: str, data: Dict[str, Any]):
        """Handle conflict resolution decisions"""
        conflict_id = data.get('conflict_id')
        resolution = data.get('resolution')  # 'accept', 'reject', 'merge'
        user_id = data.get('user_id')
        
        # Find and resolve conflict
        for conflict in self.conflict_resolution_queue:
            if conflict.get('conflict_id') == conflict_id:
                await self._apply_conflict_resolution(conflict, resolution, user_id)
                self.conflict_resolution_queue.remove(conflict)
                break
    
    async def _handle_chat_message(self, client_id: str, data: Dict[str, Any]):
        """Handle chat messages between users"""
        user_id = data.get('user_id')
        message = data.get('message')
        
        # Broadcast chat message
        event = CollaborationEvent(
            event_id=str(uuid.uuid4()),
            event_type='chat_message',
            user_id=user_id,
            timestamp=datetime.now(),
            data={'message': message, 'username': self.active_users.get(user_id, {}).get('username', 'Unknown')},
            priority=3
        )
        
        await self._broadcast_event(event)
    
    async def _broadcast_event(self, event: CollaborationEvent):
        """Broadcast event to all connected clients"""
        message = {
            'type': 'event',
            'event': asdict(event)
        }
        
        # Convert datetime to string for JSON serialization
        message['event']['timestamp'] = event.timestamp.isoformat()
        
        # Send to all connected clients
        disconnected_clients = []
        for client_id, websocket in self.websocket_clients.items():
            try:
                await websocket.send(json.dumps(message))
            except websockets.exceptions.ConnectionClosed:
                disconnected_clients.append(client_id)
        
        # Clean up disconnected clients
        for client_id in disconnected_clients:
            del self.websocket_clients[client_id]
    
    async def _notify_conflict(self, conflict: Dict[str, Any]):
        """Notify users about data conflicts"""
        message = {
            'type': 'conflict',
            'conflict': conflict
        }
        
        # Convert datetime to string
        message['conflict']['timestamp'] = conflict['timestamp'].isoformat()
        
        # Send to all connected clients
        for client_id, websocket in self.websocket_clients.items():
            try:
                await websocket.send(json.dumps(message))
            except websockets.exceptions.ConnectionClosed:
                pass
    
    async def _apply_conflict_resolution(self, conflict: Dict[str, Any], resolution: str, user_id: str):
        """Apply conflict resolution decision"""
        key = conflict['key']
        
        if resolution == 'accept':
            # Accept the proposed change
            self.shared_data[key] = conflict['proposed_value']
            self.data_versions[key] = conflict['proposed_version'] + 1
        elif resolution == 'merge':
            # Merge the changes (implement custom merge logic)
            merged_value = self._merge_data(conflict['current_value'], conflict['proposed_value'])
            self.shared_data[key] = merged_value
            self.data_versions[key] = max(conflict['current_version'], conflict['proposed_version']) + 1
        
        # Broadcast resolution
        event = CollaborationEvent(
            event_id=str(uuid.uuid4()),
            event_type='conflict_resolved',
            user_id=user_id,
            timestamp=datetime.now(),
            data={'key': key, 'resolution': resolution, 'final_value': self.shared_data[key]},
            priority=8
        )
        
        await self._broadcast_event(event)
    
    def _merge_data(self, current_value: Any, proposed_value: Any) -> Any:
        """Merge conflicting data values"""
        # Implement custom merge logic based on data type
        if isinstance(current_value, dict) and isinstance(proposed_value, dict):
            # Merge dictionaries
            merged = current_value.copy()
            merged.update(proposed_value)
            return merged
        elif isinstance(current_value, list) and isinstance(proposed_value, list):
            # Merge lists (remove duplicates)
            merged = current_value.copy()
            for item in proposed_value:
                if item not in merged:
                    merged.append(item)
            return merged
        else:
            # For other types, prefer the proposed value
            return proposed_value
    
    def _process_events(self):
        """Process collaboration events in background thread"""
        while True:
            try:
                # Process high-priority events first
                high_priority_events = [e for e in self.event_queue if e.priority >= 8]
                normal_priority_events = [e for e in self.event_queue if e.priority < 8]
                
                for event in high_priority_events + normal_priority_events:
                    self._handle_event(event)
                    self.event_queue.remove(event)
                
                time.sleep(0.1)  # Process events every 100ms
                
            except Exception as e:
                self.logger.error(f"Error processing events: {e}")
                time.sleep(1)
    
    def _handle_event(self, event: CollaborationEvent):
        """Handle individual collaboration event"""
        handlers = self.event_handlers.get(event.event_type, [])
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                self.logger.error(f"Error in event handler: {e}")
    
    def _resolve_conflicts(self):
        """Resolve conflicts in background thread"""
        while True:
            try:
                # Process conflicts with automatic resolution for simple cases
                for conflict in self.conflict_resolution_queue[:]:
                    if self._can_auto_resolve(conflict):
                        resolution = self._auto_resolve_conflict(conflict)
                        asyncio.run(self._apply_conflict_resolution(conflict, resolution, 'system'))
                        self.conflict_resolution_queue.remove(conflict)
                
                time.sleep(1)  # Check conflicts every second
                
            except Exception as e:
                self.logger.error(f"Error resolving conflicts: {e}")
                time.sleep(5)
    
    def _can_auto_resolve(self, conflict: Dict[str, Any]) -> bool:
        """Check if conflict can be automatically resolved"""
        # Auto-resolve simple conflicts (e.g., different users updating different fields)
        key = conflict['key']
        current_value = conflict['current_value']
        proposed_value = conflict['proposed_value']
        
        # If both values are dictionaries and have different keys, auto-merge
        if isinstance(current_value, dict) and isinstance(proposed_value, dict):
            current_keys = set(current_value.keys())
            proposed_keys = set(proposed_value.keys())
            return len(current_keys.intersection(proposed_keys)) == 0
        
        return False
    
    def _auto_resolve_conflict(self, conflict: Dict[str, Any]) -> str:
        """Automatically resolve conflict"""
        return 'merge'  # Default to merge for auto-resolution
    
    def _monitor_user_activity(self):
        """Monitor user activity in background thread"""
        while True:
            try:
                current_time = datetime.now()
                
                for user_id, session in self.active_users.items():
                    # Update user status based on activity
                    time_since_activity = current_time - session.last_activity
                    
                    if time_since_activity > timedelta(minutes=30):
                        session.status = 'away'
                    elif time_since_activity > timedelta(minutes=5):
                        session.status = 'idle'
                    else:
                        session.status = 'active'
                
                time.sleep(30)  # Check activity every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Error monitoring user activity: {e}")
                time.sleep(60)
    
    def register_event_handler(self, event_type: str, handler: Callable):
        """Register event handler for specific event type"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
    
    def assign_task(self, task_type: str, description: str, assigned_to: str = None, 
                   priority: int = 5, deadline: datetime = None) -> str:
        """Assign a new task to a user"""
        task_id = str(uuid.uuid4())
        
        # Auto-assign if no user specified
        if assigned_to is None:
            available_users = [uid for uid, session in self.active_users.items() 
                            if session.status == 'active' and session.current_task is None]
            if available_users:
                assigned_to = available_users[0]
            else:
                assigned_to = 'unassigned'
        
        task = TaskAssignment(
            task_id=task_id,
            task_type=task_type,
            assigned_to=assigned_to,
            assigned_at=datetime.now(),
            deadline=deadline,
            status='pending',
            priority=priority,
            description=description,
            progress=0.0
        )
        
        self.task_queue.append(task)
        
        # Update user's current task
        if assigned_to in self.active_users:
            self.active_users[assigned_to].current_task = task_id
        
        return task_id
    
    def get_active_users(self) -> List[Dict[str, Any]]:
        """Get list of active users"""
        return [asdict(session) for session in self.active_users.values()]
    
    def get_task_queue(self) -> List[Dict[str, Any]]:
        """Get current task queue"""
        return [asdict(task) for task in self.task_queue]
    
    def get_shared_data(self) -> Dict[str, Any]:
        """Get current shared data"""
        return self.shared_data.copy()
    
    def update_user_activity(self, user_id: str):
        """Update user activity timestamp"""
        if user_id in self.active_users:
            self.active_users[user_id].last_activity = datetime.now()
    
    def save_to_database(self):
        """Save collaboration state to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Save user sessions
            for user_id, session in self.active_users.items():
                cursor.execute('''
                    INSERT OR REPLACE INTO user_sessions 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    user_id, session.username, session.session_id,
                    session.connected_at.isoformat(),
                    session.last_activity.isoformat(),
                    json.dumps(session.permissions),
                    session.current_task, session.status
                ))
            
            # Save shared data
            for key, value in self.shared_data.items():
                cursor.execute('''
                    INSERT OR REPLACE INTO shared_data 
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    key, json.dumps(value), self.data_versions.get(key, 0),
                    datetime.now().isoformat(), 'system'
                ))
            
            # Save task assignments
            for task in self.task_queue:
                cursor.execute('''
                    INSERT OR REPLACE INTO task_assignments 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    task.task_id, task.task_type, task.assigned_to,
                    task.assigned_at.isoformat(),
                    task.deadline.isoformat() if task.deadline else None,
                    task.status, task.priority, task.description, task.progress
                ))
            
            conn.commit()
            
        except Exception as e:
            self.logger.error(f"Error saving to database: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def load_from_database(self):
        """Load collaboration state from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Load shared data
            cursor.execute('SELECT key, value, version FROM shared_data')
            for key, value, version in cursor.fetchall():
                self.shared_data[key] = json.loads(value)
                self.data_versions[key] = version
            
            # Load task assignments
            cursor.execute('''
                SELECT task_id, task_type, assigned_to, assigned_at, deadline,
                       status, priority, description, progress 
                FROM task_assignments WHERE status != 'completed'
            ''')
            
            for row in cursor.fetchall():
                task = TaskAssignment(
                    task_id=row[0], task_type=row[1], assigned_to=row[2],
                    assigned_at=datetime.fromisoformat(row[3]),
                    deadline=datetime.fromisoformat(row[4]) if row[4] else None,
                    status=row[5], priority=row[6], description=row[7], progress=row[8]
                )
                self.task_queue.append(task)
            
        except Exception as e:
            self.logger.error(f"Error loading from database: {e}")
        finally:
            conn.close() 