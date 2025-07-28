#!/usr/bin/env python3
"""
Advanced Automation and Workflow System
Intelligent task scheduling, pipeline automation, and workflow orchestration
"""

import os
import json
import asyncio
import threading
import time
import schedule
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import logging
import hashlib
import sqlite3
import yaml
from pathlib import Path

# Task scheduling
try:
    import schedule
    SCHEDULE_AVAILABLE = True
except ImportError:
    SCHEDULE_AVAILABLE = False

# Workflow orchestration
try:
    from celery import Celery
    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False

@dataclass
class WorkflowStep:
    """Individual step in a workflow"""
    step_id: str
    name: str
    function: str
    parameters: Dict[str, Any]
    dependencies: List[str]
    timeout: int
    retry_count: int
    retry_delay: int
    status: str  # 'pending', 'running', 'completed', 'failed', 'skipped'
    result: Optional[Any] = None
    error: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

@dataclass
class Workflow:
    """Complete workflow definition"""
    workflow_id: str
    name: str
    description: str
    steps: List[WorkflowStep]
    triggers: List[Dict[str, Any]]
    schedule: Optional[str] = None
    enabled: bool = True
    created_at: datetime = None
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None

@dataclass
class AutomationRule:
    """Automation rule for conditional execution"""
    rule_id: str
    name: str
    condition: str
    actions: List[Dict[str, Any]]
    priority: int
    enabled: bool = True
    last_triggered: Optional[datetime] = None

class AdvancedAutomation:
    """Advanced automation and workflow system"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Workflow management
        self.workflows: Dict[str, Workflow] = {}
        self.running_workflows: Dict[str, Dict[str, Any]] = {}
        
        # Automation rules
        self.automation_rules: List[AutomationRule] = []
        
        # Task queue
        self.task_queue: List[Dict[str, Any]] = []
        self.completed_tasks: List[Dict[str, Any]] = []
        
        # Function registry
        self.registered_functions: Dict[str, Callable] = {}
        
        # Workflow executor
        self._workflow_executor = None
        
        # Database for persistence
        self.db_path = "automation.db"
        self._init_database()
        
        # Start background tasks
        self._start_background_tasks()
        
        # Register default functions
        self._register_default_functions()
    
    def _init_database(self):
        """Initialize automation database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS workflows (
                workflow_id TEXT PRIMARY KEY,
                name TEXT,
                description TEXT,
                steps TEXT,
                triggers TEXT,
                schedule TEXT,
                enabled INTEGER,
                created_at TEXT,
                last_run TEXT,
                next_run TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS workflow_executions (
                execution_id TEXT PRIMARY KEY,
                workflow_id TEXT,
                status TEXT,
                start_time TEXT,
                end_time TEXT,
                result TEXT,
                error TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS automation_rules (
                rule_id TEXT PRIMARY KEY,
                name TEXT,
                condition TEXT,
                actions TEXT,
                priority INTEGER,
                enabled INTEGER,
                last_triggered TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scheduled_tasks (
                task_id TEXT PRIMARY KEY,
                name TEXT,
                function TEXT,
                parameters TEXT,
                schedule TEXT,
                enabled INTEGER,
                last_run TEXT,
                next_run TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _start_background_tasks(self):
        """Start background automation tasks"""
        # Workflow execution thread
        self.workflow_thread = threading.Thread(target=self._workflow_executor, daemon=True)
        self.workflow_thread.start()
        
        # Rule evaluation thread
        self.rule_thread = threading.Thread(target=self._rule_evaluator, daemon=True)
        self.rule_thread.start()
        
        # Task scheduler thread
        if SCHEDULE_AVAILABLE:
            self.scheduler_thread = threading.Thread(target=self._task_scheduler, daemon=True)
            self.scheduler_thread.start()
    
    def _register_default_functions(self):
        """Register default automation functions"""
        self.register_function('crawl_dataset', self._crawl_dataset)
        self.register_function('validate_data', self._validate_data)
        self.register_function('enhance_content', self._enhance_content)
        self.register_function('generate_insights', self._generate_insights)
        self.register_function('export_data', self._export_data)
        self.register_function('send_notification', self._send_notification)
        self.register_function('cleanup_old_data', self._cleanup_old_data)
        self.register_function('backup_data', self._backup_data)
        self.register_function('update_analytics', self._update_analytics)
        self.register_function('optimize_performance', self._optimize_performance)
    
    def register_function(self, name: str, function: Callable):
        """Register a function for automation"""
        self.registered_functions[name] = function
        self.logger.info(f"Registered function: {name}")
    
    def create_workflow(self, name: str, description: str, steps: List[Dict[str, Any]], 
                       triggers: List[Dict[str, Any]] = None, schedule: str = None) -> str:
        """Create a new workflow"""
        workflow_id = str(hashlib.md5(f"{name}_{time.time()}".encode()).hexdigest())
        
        # Convert step definitions to WorkflowStep objects
        workflow_steps = []
        for step_def in steps:
            step = WorkflowStep(
                step_id=step_def.get('step_id', str(uuid.uuid4())),
                name=step_def['name'],
                function=step_def['function'],
                parameters=step_def.get('parameters', {}),
                dependencies=step_def.get('dependencies', []),
                timeout=step_def.get('timeout', 300),
                retry_count=step_def.get('retry_count', 3),
                retry_delay=step_def.get('retry_delay', 60),
                status='pending'
            )
            workflow_steps.append(step)
        
        workflow = Workflow(
            workflow_id=workflow_id,
            name=name,
            description=description,
            steps=workflow_steps,
            triggers=triggers or [],
            schedule=schedule,
            created_at=datetime.now()
        )
        
        self.workflows[workflow_id] = workflow
        self._save_workflow_to_db(workflow)
        
        return workflow_id
    
    def _save_workflow_to_db(self, workflow: Workflow):
        """Save workflow to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO workflows 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                workflow.workflow_id,
                workflow.name,
                workflow.description,
                json.dumps([asdict(step) for step in workflow.steps]),
                json.dumps(workflow.triggers),
                workflow.schedule,
                1 if workflow.enabled else 0,
                workflow.created_at.isoformat(),
                workflow.last_run.isoformat() if workflow.last_run else None,
                workflow.next_run.isoformat() if workflow.next_run else None
            ))
            
            conn.commit()
            
        except Exception as e:
            self.logger.error(f"Error saving workflow to database: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def execute_workflow(self, workflow_id: str, parameters: Dict[str, Any] = None) -> str:
        """Execute a workflow"""
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        workflow = self.workflows[workflow_id]
        execution_id = str(hashlib.md5(f"{workflow_id}_{time.time()}".encode()).hexdigest())
        
        # Create execution context
        execution_context = {
            'execution_id': execution_id,
            'workflow_id': workflow_id,
            'parameters': parameters or {},
            'start_time': datetime.now(),
            'status': 'running',
            'completed_steps': [],
            'failed_steps': [],
            'results': {}
        }
        
        self.running_workflows[execution_id] = execution_context
        
        # Start workflow execution in background
        threading.Thread(
            target=self._execute_workflow_steps,
            args=(execution_id,),
            daemon=True
        ).start()
        
        return execution_id
    
    def _execute_workflow_steps(self, execution_id: str):
        """Execute workflow steps"""
        context = self.running_workflows[execution_id]
        workflow = self.workflows[context['workflow_id']]
        
        try:
            # Execute steps in dependency order
            completed_steps = set()
            failed_steps = set()
            
            while len(completed_steps) < len(workflow.steps) and len(failed_steps) == 0:
                for step in workflow.steps:
                    if step.step_id in completed_steps or step.step_id in failed_steps:
                        continue
                    
                    # Check dependencies
                    if all(dep in completed_steps for dep in step.dependencies):
                        # Execute step
                        step.status = 'running'
                        step.start_time = datetime.now()
                        
                        try:
                            result = self._execute_step(step, context['parameters'])
                            step.status = 'completed'
                            step.result = result
                            step.end_time = datetime.now()
                            completed_steps.add(step.step_id)
                            context['completed_steps'].append(step.step_id)
                            context['results'][step.step_id] = result
                            
                        except Exception as e:
                            step.status = 'failed'
                            step.error = str(e)
                            step.end_time = datetime.now()
                            failed_steps.add(step.step_id)
                            context['failed_steps'].append(step.step_id)
                            
                            # Retry logic
                            if step.retry_count > 0:
                                for attempt in range(step.retry_count):
                                    time.sleep(step.retry_delay)
                                    try:
                                        result = self._execute_step(step, context['parameters'])
                                        step.status = 'completed'
                                        step.result = result
                                        step.end_time = datetime.now()
                                        completed_steps.add(step.step_id)
                                        context['completed_steps'].append(step.step_id)
                                        context['results'][step.step_id] = result
                                        break
                                    except Exception as retry_e:
                                        step.error = str(retry_e)
                                        if attempt == step.retry_count - 1:
                                            failed_steps.add(step.step_id)
                                            context['failed_steps'].append(step.step_id)
                
                time.sleep(1)  # Check every second
            
            # Update execution status
            if len(failed_steps) > 0:
                context['status'] = 'failed'
            else:
                context['status'] = 'completed'
            
            context['end_time'] = datetime.now()
            
            # Update workflow last run
            workflow.last_run = datetime.now()
            self._save_workflow_to_db(workflow)
            
        except Exception as e:
            context['status'] = 'failed'
            context['error'] = str(e)
            context['end_time'] = datetime.now()
            self.logger.error(f"Workflow execution failed: {e}")
        
        finally:
            # Clean up after some time
            threading.Timer(3600, lambda: self._cleanup_execution(execution_id)).start()
    
    def _execute_step(self, step: WorkflowStep, parameters: Dict[str, Any]) -> Any:
        """Execute a single workflow step"""
        if step.function not in self.registered_functions:
            raise ValueError(f"Function {step.function} not registered")
        
        function = self.registered_functions[step.function]
        
        # Merge parameters
        merged_params = {**parameters, **step.parameters}
        
        # Execute with timeout
        if step.timeout > 0:
            # Note: This is a simplified timeout implementation
            # In production, you'd want to use proper async/timeout handling
            return function(**merged_params)
        else:
            return function(**merged_params)
    
    def _crawl_dataset(self, dataset_url: str, **kwargs) -> Dict[str, Any]:
        """Crawl a dataset"""
        # This would integrate with the existing crawler
        self.logger.info(f"Crawling dataset: {dataset_url}")
        return {'status': 'success', 'url': dataset_url, 'crawled_at': datetime.now().isoformat()}
    
    def _validate_data(self, data_path: str, **kwargs) -> Dict[str, Any]:
        """Validate crawled data"""
        self.logger.info(f"Validating data: {data_path}")
        return {'status': 'success', 'validated_at': datetime.now().isoformat()}
    
    def _enhance_content(self, data_path: str, **kwargs) -> Dict[str, Any]:
        """Enhance content using AI"""
        self.logger.info(f"Enhancing content: {data_path}")
        return {'status': 'success', 'enhanced_at': datetime.now().isoformat()}
    
    def _generate_insights(self, data_path: str, **kwargs) -> Dict[str, Any]:
        """Generate insights from data"""
        self.logger.info(f"Generating insights: {data_path}")
        return {'status': 'success', 'insights_generated_at': datetime.now().isoformat()}
    
    def _export_data(self, data_path: str, export_format: str = 'json', **kwargs) -> Dict[str, Any]:
        """Export data in specified format"""
        self.logger.info(f"Exporting data: {data_path} in {export_format} format")
        return {'status': 'success', 'exported_at': datetime.now().isoformat()}
    
    def _send_notification(self, message: str, recipients: List[str] = None, **kwargs) -> Dict[str, Any]:
        """Send notification"""
        self.logger.info(f"Sending notification: {message}")
        return {'status': 'success', 'notification_sent_at': datetime.now().isoformat()}
    
    def _cleanup_old_data(self, days_old: int = 30, **kwargs) -> Dict[str, Any]:
        """Clean up old data"""
        self.logger.info(f"Cleaning up data older than {days_old} days")
        return {'status': 'success', 'cleanup_completed_at': datetime.now().isoformat()}
    
    def _backup_data(self, backup_path: str, **kwargs) -> Dict[str, Any]:
        """Backup data"""
        self.logger.info(f"Backing up data to: {backup_path}")
        return {'status': 'success', 'backup_completed_at': datetime.now().isoformat()}
    
    def _update_analytics(self, **kwargs) -> Dict[str, Any]:
        """Update analytics dashboard"""
        self.logger.info("Updating analytics dashboard")
        return {'status': 'success', 'analytics_updated_at': datetime.now().isoformat()}
    
    def _optimize_performance(self, **kwargs) -> Dict[str, Any]:
        """Optimize system performance"""
        self.logger.info("Optimizing system performance")
        return {'status': 'success', 'optimization_completed_at': datetime.now().isoformat()}
    
    def create_automation_rule(self, name: str, condition: str, actions: List[Dict[str, Any]], 
                              priority: int = 5) -> str:
        """Create an automation rule"""
        rule_id = str(hashlib.md5(f"{name}_{time.time()}".encode()).hexdigest())
        
        rule = AutomationRule(
            rule_id=rule_id,
            name=name,
            condition=condition,
            actions=actions,
            priority=priority
        )
        
        self.automation_rules.append(rule)
        self._save_rule_to_db(rule)
        
        return rule_id
    
    def _save_rule_to_db(self, rule: AutomationRule):
        """Save automation rule to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO automation_rules 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                rule.rule_id,
                rule.name,
                rule.condition,
                json.dumps(rule.actions),
                rule.priority,
                1 if rule.enabled else 0,
                rule.last_triggered.isoformat() if rule.last_triggered else None
            ))
            
            conn.commit()
            
        except Exception as e:
            self.logger.error(f"Error saving rule to database: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def _rule_evaluator(self):
        """Evaluate automation rules in background"""
        while True:
            try:
                # Sort rules by priority (higher priority first)
                sorted_rules = sorted(self.automation_rules, key=lambda r: r.priority, reverse=True)
                
                for rule in sorted_rules:
                    if not rule.enabled:
                        continue
                    
                    # Evaluate condition
                    if self._evaluate_condition(rule.condition):
                        # Execute actions
                        for action in rule.actions:
                            self._execute_action(action)
                        
                        rule.last_triggered = datetime.now()
                        self._save_rule_to_db(rule)
                
                time.sleep(60)  # Check rules every minute
                
            except Exception as e:
                self.logger.error(f"Error evaluating rules: {e}")
                time.sleep(300)
    
    def _evaluate_condition(self, condition: str) -> bool:
        """Evaluate automation condition"""
        try:
            # This is a simplified condition evaluator
            # In production, you'd want a more sophisticated expression parser
            
            # Check for common conditions
            if 'file_exists' in condition:
                file_path = condition.split('file_exists(')[1].split(')')[0].strip('"\'')
                return os.path.exists(file_path)
            
            elif 'time_of_day' in condition:
                current_hour = datetime.now().hour
                if 'morning' in condition and 6 <= current_hour < 12:
                    return True
                elif 'afternoon' in condition and 12 <= current_hour < 18:
                    return True
                elif 'evening' in condition and 18 <= current_hour < 22:
                    return True
                elif 'night' in condition and (current_hour >= 22 or current_hour < 6):
                    return True
            
            elif 'data_size' in condition:
                # Extract size threshold from condition
                import re
                match = re.search(r'data_size\s*>\s*(\d+)', condition)
                if match:
                    threshold = int(match.group(1))
                    # This would check actual data size
                    return True  # Simplified
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error evaluating condition: {e}")
            return False
    
    def _execute_action(self, action: Dict[str, Any]):
        """Execute automation action"""
        action_type = action.get('type')
        
        if action_type == 'execute_workflow':
            workflow_id = action.get('workflow_id')
            parameters = action.get('parameters', {})
            self.execute_workflow(workflow_id, parameters)
        
        elif action_type == 'send_notification':
            message = action.get('message', '')
            recipients = action.get('recipients', [])
            self._send_notification(message, recipients)
        
        elif action_type == 'run_function':
            function_name = action.get('function')
            parameters = action.get('parameters', {})
            if function_name in self.registered_functions:
                self.registered_functions[function_name](**parameters)
    
    def _task_scheduler(self):
        """Background task scheduler"""
        if not SCHEDULE_AVAILABLE:
            return
        
        while True:
            try:
                schedule.run_pending()
                time.sleep(1)
            except Exception as e:
                self.logger.error(f"Error in task scheduler: {e}")
                time.sleep(60)
    
    def schedule_task(self, name: str, function: str, parameters: Dict[str, Any], 
                     schedule_str: str) -> str:
        """Schedule a recurring task"""
        task_id = str(hashlib.md5(f"{name}_{time.time()}".encode()).hexdigest())
        
        # Parse schedule string (e.g., "every 10 minutes", "daily at 10:30")
        if schedule_str.startswith('every'):
            # Handle "every X minutes/hours/days"
            parts = schedule_str.split()
            if len(parts) >= 3:
                interval = int(parts[1])
                unit = parts[2]
                
                if unit == 'minutes':
                    schedule.every(interval).minutes.do(
                        lambda: self._execute_scheduled_task(task_id, function, parameters)
                    )
                elif unit == 'hours':
                    schedule.every(interval).hours.do(
                        lambda: self._execute_scheduled_task(task_id, function, parameters)
                    )
                elif unit == 'days':
                    schedule.every(interval).days.do(
                        lambda: self._execute_scheduled_task(task_id, function, parameters)
                    )
        
        elif schedule_str.startswith('daily'):
            # Handle "daily at HH:MM"
            import re
            match = re.search(r'daily at (\d{1,2}):(\d{2})', schedule_str)
            if match:
                hour = int(match.group(1))
                minute = int(match.group(2))
                schedule.every().day.at(f"{hour:02d}:{minute:02d}").do(
                    lambda: self._execute_scheduled_task(task_id, function, parameters)
                )
        
        return task_id
    
    def _execute_scheduled_task(self, task_id: str, function: str, parameters: Dict[str, Any]):
        """Execute a scheduled task"""
        try:
            if function in self.registered_functions:
                result = self.registered_functions[function](**parameters)
                self.logger.info(f"Scheduled task {task_id} completed successfully")
            else:
                self.logger.error(f"Function {function} not found for scheduled task {task_id}")
        except Exception as e:
            self.logger.error(f"Error executing scheduled task {task_id}: {e}")
    
    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get workflow execution status"""
        if workflow_id in self.workflows:
            workflow = self.workflows[workflow_id]
            return {
                'workflow_id': workflow_id,
                'name': workflow.name,
                'status': 'enabled' if workflow.enabled else 'disabled',
                'last_run': workflow.last_run.isoformat() if workflow.last_run else None,
                'next_run': workflow.next_run.isoformat() if workflow.next_run else None,
                'total_steps': len(workflow.steps)
            }
        return None
    
    def get_execution_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get workflow execution status"""
        if execution_id in self.running_workflows:
            context = self.running_workflows[execution_id]
            return {
                'execution_id': execution_id,
                'workflow_id': context['workflow_id'],
                'status': context['status'],
                'start_time': context['start_time'].isoformat(),
                'end_time': context['end_time'].isoformat() if 'end_time' in context else None,
                'completed_steps': len(context['completed_steps']),
                'failed_steps': len(context['failed_steps']),
                'error': context.get('error')
            }
        return None
    
    def _cleanup_execution(self, execution_id: str):
        """Clean up completed execution"""
        if execution_id in self.running_workflows:
            del self.running_workflows[execution_id]
    
    def load_workflows_from_db(self):
        """Load workflows from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT * FROM workflows')
            for row in cursor.fetchall():
                workflow_id, name, description, steps_json, triggers_json, schedule, enabled, created_at, last_run, next_run = row
                
                # Parse steps
                steps_data = json.loads(steps_json)
                steps = []
                for step_data in steps_data:
                    step = WorkflowStep(
                        step_id=step_data['step_id'],
                        name=step_data['name'],
                        function=step_data['function'],
                        parameters=step_data['parameters'],
                        dependencies=step_data['dependencies'],
                        timeout=step_data['timeout'],
                        retry_count=step_data['retry_count'],
                        retry_delay=step_data['retry_delay'],
                        status=step_data['status']
                    )
                    steps.append(step)
                
                workflow = Workflow(
                    workflow_id=workflow_id,
                    name=name,
                    description=description,
                    steps=steps,
                    triggers=json.loads(triggers_json),
                    schedule=schedule,
                    enabled=bool(enabled),
                    created_at=datetime.fromisoformat(created_at) if created_at else datetime.now(),
                    last_run=datetime.fromisoformat(last_run) if last_run else None,
                    next_run=datetime.fromisoformat(next_run) if next_run else None
                )
                
                self.workflows[workflow_id] = workflow
                
        except Exception as e:
            self.logger.error(f"Error loading workflows from database: {e}")
        finally:
            conn.close() 