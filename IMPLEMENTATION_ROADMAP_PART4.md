# 🚀 Implementation Roadmap - Part 4: Automation, Enterprise & Scale (Final)

## 🔄 PHASE 9: Automation & Workflows (Weeks 49-56)

**Goal:** Enable automated workflows and integrations
**Dependencies:** Phase 7 (AI features), Phase 8 (analytics)
**Deliverables:** Workflow engine, integration platform

### 9.1 Workflow Engine (Week 49-50)

#### Workflow Definition System
```python
# src/spotify_mcp/automation/workflow.py
from typing import Dict, List, Callable, Any
from datetime import datetime, timedelta
from enum import Enum

class TriggerType(Enum):
    SCHEDULE = "schedule"  # Cron-like scheduling
    EVENT = "event"  # When something happens
    CONDITION = "condition"  # When condition met

class Workflow:
    """Define and execute automated workflows"""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.triggers = []
        self.conditions = []
        self.actions = []
        self.enabled = True

    def on_schedule(self, cron: str):
        """Trigger on schedule (cron expression)"""
        self.triggers.append({
            'type': TriggerType.SCHEDULE,
            'cron': cron
        })
        return self

    def on_event(self, event_type: str):
        """Trigger on specific event"""
        self.triggers.append({
            'type': TriggerType.EVENT,
            'event_type': event_type
        })
        return self

    def when(self, condition: Callable):
        """Add condition that must be met"""
        self.conditions.append(condition)
        return self

    def then(self, action: Callable):
        """Add action to execute"""
        self.actions.append(action)
        return self

    async def execute(self, context: Dict[str, Any]) -> Dict:
        """Execute workflow"""

        # Check conditions
        for condition in self.conditions:
            if not await condition(context):
                return {'status': 'skipped', 'reason': 'conditions not met'}

        # Execute actions
        results = []
        for action in self.actions:
            try:
                result = await action(context)
                results.append({'status': 'success', 'result': result})
            except Exception as e:
                results.append({'status': 'error', 'error': str(e)})

        return {
            'status': 'completed',
            'workflow': self.name,
            'executed_at': datetime.utcnow().isoformat(),
            'results': results
        }

class WorkflowEngine:
    """Manage and execute workflows"""

    def __init__(self, spotify_client):
        self.client = spotify_client
        self.workflows = {}
        self.scheduler = BackgroundScheduler()

    def register_workflow(self, workflow: Workflow):
        """Register a workflow"""
        self.workflows[workflow.name] = workflow

        # Schedule if it has schedule triggers
        for trigger in workflow.triggers:
            if trigger['type'] == TriggerType.SCHEDULE:
                self.scheduler.add_job(
                    lambda: self._execute_workflow(workflow.name),
                    'cron',
                    **self._parse_cron(trigger['cron'])
                )

    async def _execute_workflow(self, workflow_name: str):
        """Execute a workflow by name"""
        workflow = self.workflows.get(workflow_name)
        if workflow and workflow.enabled:
            context = await self._build_context()
            return await workflow.execute(context)

    async def _build_context(self) -> Dict:
        """Build execution context with current state"""
        return {
            'current_time': datetime.utcnow(),
            'user': await self.client.current_user(),
            'playback': await self.client.current_playback(),
        }

# Example workflows
def create_example_workflows(engine: WorkflowEngine, client):
    """Create example workflows"""

    # 1. Weekly Discover Playlist
    (Workflow("weekly_discover", "Create weekly discovery playlist")
     .on_schedule("0 9 * * MON")  # Every Monday at 9 AM
     .then(lambda ctx: create_discovery_playlist(client)))

    # 2. Liked Songs to Playlist
    (Workflow("save_liked_songs", "Add liked songs to monthly playlist")
     .on_event("track_liked")
     .then(lambda ctx: add_to_monthly_playlist(client, ctx['track'])))

    # 3. Remove Skipped Songs
    (Workflow("cleanup_skipped", "Remove frequently skipped songs")
     .on_schedule("0 2 * * SUN")  # Sunday 2 AM
     .then(lambda ctx: remove_skipped_songs(client)))

    # 4. Workout Playlist Refresh
    (Workflow("refresh_workout", "Refresh workout playlist with new music")
     .on_schedule("0 8 * * MON,WED,FRI")
     .then(lambda ctx: refresh_workout_playlist(client)))

    # 5. Bedtime Auto-Play
    (Workflow("bedtime_music", "Auto-play sleep music at bedtime")
     .on_schedule("0 22 * * *")  # 10 PM daily
     .when(lambda ctx: is_device_active(client))
     .then(lambda ctx: play_sleep_playlist(client)))
```

### 9.2 Integration Framework (Week 51-52)

#### Zapier-Style Integration Platform
```python
# src/spotify_mcp/integrations/platform.py
from typing import Dict, List, Any, Callable
from abc import ABC, abstractmethod

class Integration(ABC):
    """Base class for integrations"""

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    async def authenticate(self, credentials: Dict) -> bool:
        pass

    @abstractmethod
    async def get_triggers(self) -> List[Dict]:
        """Get available triggers"""
        pass

    @abstractmethod
    async def get_actions(self) -> List[Dict]:
        """Get available actions"""
        pass

class LastFMIntegration(Integration):
    """Last.fm scrobbling integration"""

    name = "lastfm"

    def __init__(self):
        self.api_key = None
        self.session_key = None

    async def authenticate(self, credentials: Dict) -> bool:
        self.api_key = credentials['api_key']
        self.session_key = credentials['session_key']
        return True

    async def get_triggers(self) -> List[Dict]:
        return []  # Last.fm is action-only

    async def get_actions(self) -> List[Dict]:
        return [
            {
                'id': 'scrobble',
                'name': 'Scrobble Track',
                'description': 'Submit track to Last.fm',
                'parameters': ['artist', 'track', 'timestamp']
            }
        ]

    async def scrobble(self, artist: str, track: str, timestamp: int):
        """Scrobble a track to Last.fm"""
        # Implementation using pylast
        pass

class DiscordIntegration(Integration):
    """Discord Rich Presence integration"""

    name = "discord"

    async def get_actions(self) -> List[Dict]:
        return [
            {
                'id': 'update_presence',
                'name': 'Update Rich Presence',
                'description': 'Show what you\'re playing on Discord',
                'parameters': ['state', 'details', 'large_image']
            }
        ]

    async def update_presence(self, state: str, details: str, large_image: str = None):
        """Update Discord Rich Presence"""
        from pypresence import Presence

        rpc = Presence(client_id="your_client_id")
        rpc.connect()

        rpc.update(
            state=state,
            details=details,
            large_image=large_image
        )

class NotionIntegration(Integration):
    """Notion integration for music journaling"""

    name = "notion"

    async def get_actions(self) -> List[Dict]:
        return [
            {
                'id': 'log_track',
                'name': 'Log to Notion',
                'description': 'Add track to Notion music journal',
                'parameters': ['track', 'notes']
            }
        ]

    async def log_track(self, track: Dict, notes: str = ""):
        """Add track to Notion database"""
        # Implementation using notion-client
        pass

class IntegrationManager:
    """Manage all integrations"""

    def __init__(self):
        self.integrations = {}
        self._register_builtin_integrations()

    def _register_builtin_integrations(self):
        """Register built-in integrations"""
        self.register(LastFMIntegration())
        self.register(DiscordIntegration())
        self.register(NotionIntegration())

    def register(self, integration: Integration):
        """Register an integration"""
        self.integrations[integration.name] = integration

    def get_integration(self, name: str) -> Integration:
        """Get integration by name"""
        return self.integrations.get(name)

    async def execute_action(
        self,
        integration_name: str,
        action_id: str,
        parameters: Dict
    ) -> Any:
        """Execute an integration action"""

        integration = self.get_integration(integration_name)
        if not integration:
            raise ValueError(f"Integration {integration_name} not found")

        action = getattr(integration, action_id)
        return await action(**parameters)
```

### 9.3 Smart Automation Rules (Week 53-54)

#### Rule-Based Automation
```python
# src/spotify_mcp/automation/rules.py
from typing import List, Dict, Callable

class AutomationRule:
    """Define automation rules"""

    def __init__(self, name: str):
        self.name = name
        self.enabled = True

    async def should_execute(self, context: Dict) -> bool:
        """Check if rule should execute"""
        raise NotImplementedError

    async def execute(self, context: Dict):
        """Execute the rule"""
        raise NotImplementedError

class PlaylistCleanupRule(AutomationRule):
    """Remove songs you always skip from playlists"""

    def __init__(self, skip_threshold: int = 3):
        super().__init__("Playlist Cleanup")
        self.skip_threshold = skip_threshold

    async def should_execute(self, context: Dict) -> bool:
        # Execute weekly
        return context['day_of_week'] == 0  # Monday

    async def execute(self, context: Dict):
        """Remove frequently skipped tracks"""

        # Get skip data
        skip_counts = await self._get_skip_counts(context['user_id'])

        # Get user's playlists
        playlists = await context['client'].get_user_playlists()

        removed_count = 0

        for playlist in playlists['items']:
            # Skip if not owned by user
            if playlist['owner']['id'] != context['user_id']:
                continue

            # Get tracks
            tracks = await context['client'].get_playlist_tracks(playlist['id'])

            tracks_to_remove = []

            for item in tracks['items']:
                track_id = item['track']['id']
                if skip_counts.get(track_id, 0) >= self.skip_threshold:
                    tracks_to_remove.append(item['track']['uri'])

            # Remove tracks
            if tracks_to_remove:
                await context['client'].remove_tracks_from_playlist(
                    playlist['id'],
                    tracks_to_remove
                )
                removed_count += len(tracks_to_remove)

        return {
            'removed_tracks': removed_count,
            'message': f"Removed {removed_count} frequently skipped tracks"
        }

class DuplicateRemovalRule(AutomationRule):
    """Remove duplicate songs from playlists"""

    def __init__(self):
        super().__init__("Remove Duplicates")

    async def execute(self, context: Dict):
        """Remove duplicates from all playlists"""

        playlists = await context['client'].get_user_playlists()
        total_removed = 0

        for playlist in playlists['items']:
            if playlist['owner']['id'] != context['user_id']:
                continue

            tracks = await context['client'].get_playlist_tracks(playlist['id'])

            seen_ids = set()
            duplicates = []

            for i, item in enumerate(tracks['items']):
                track_id = item['track']['id']

                if track_id in seen_ids:
                    duplicates.append({
                        'uri': item['track']['uri'],
                        'positions': [i]
                    })
                else:
                    seen_ids.add(track_id)

            if duplicates:
                await context['client'].remove_tracks_from_playlist(
                    playlist['id'],
                    duplicates
                )
                total_removed += len(duplicates)

        return {
            'removed_duplicates': total_removed,
            'message': f"Removed {total_removed} duplicate tracks"
        }

class BackupLibraryRule(AutomationRule):
    """Backup library to JSON weekly"""

    async def execute(self, context: Dict):
        """Create backup of user's library"""

        # Get all data
        saved_tracks = await context['client'].get_all_saved_tracks()
        playlists = await context['client'].get_user_playlists()
        following = await context['client'].get_followed_artists()

        backup = {
            'created_at': datetime.utcnow().isoformat(),
            'user_id': context['user_id'],
            'saved_tracks': saved_tracks,
            'playlists': playlists,
            'following_artists': following
        }

        # Save to file
        filename = f"backup_{datetime.utcnow().strftime('%Y%m%d')}.json"
        with open(filename, 'w') as f:
            json.dump(backup, f, indent=2)

        # Also upload to cloud storage
        await self._upload_to_cloud(filename, backup)

        return {
            'backup_file': filename,
            'tracks_count': len(saved_tracks),
            'playlists_count': len(playlists)
        }
```

### 9.4 Scheduled Tasks & Cron Jobs (Week 55-56)

#### Task Scheduler
```python
# src/spotify_mcp/automation/scheduler.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class TaskScheduler:
    """Manage scheduled tasks"""

    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.tasks = {}

    def start(self):
        """Start the scheduler"""
        self.scheduler.start()
        logger.info("Task scheduler started")

    def stop(self):
        """Stop the scheduler"""
        self.scheduler.shutdown()

    def schedule_task(
        self,
        task_id: str,
        func: Callable,
        cron_expression: str,
        **kwargs
    ):
        """Schedule a task with cron expression"""

        # Parse cron expression
        # Format: minute hour day month day_of_week
        minute, hour, day, month, day_of_week = cron_expression.split()

        trigger = CronTrigger(
            minute=minute,
            hour=hour,
            day=day,
            month=month,
            day_of_week=day_of_week
        )

        job = self.scheduler.add_job(
            func,
            trigger=trigger,
            id=task_id,
            kwargs=kwargs,
            replace_existing=True
        )

        self.tasks[task_id] = {
            'function': func.__name__,
            'schedule': cron_expression,
            'next_run': job.next_run_time
        }

        logger.info(f"Scheduled task: {task_id} with cron: {cron_expression}")

    def remove_task(self, task_id: str):
        """Remove a scheduled task"""
        self.scheduler.remove_job(task_id)
        del self.tasks[task_id]

    def get_tasks(self) -> Dict:
        """Get all scheduled tasks"""
        return self.tasks

# Predefined scheduled tasks
async def setup_default_tasks(scheduler: TaskScheduler, client):
    """Setup default scheduled tasks"""

    # Daily: Backup library
    scheduler.schedule_task(
        'daily_backup',
        backup_library,
        '0 2 * * *',  # 2 AM daily
        client=client
    )

    # Weekly: Create Discover playlist
    scheduler.schedule_task(
        'weekly_discover',
        create_discover_playlist,
        '0 9 * * MON',  # Monday 9 AM
        client=client
    )

    # Monthly: Generate analytics report
    scheduler.schedule_task(
        'monthly_analytics',
        generate_monthly_report,
        '0 10 1 * *',  # 1st of month, 10 AM
        client=client
    )

    # Weekly: Cleanup playlists
    scheduler.schedule_task(
        'weekly_cleanup',
        cleanup_playlists,
        '0 3 * * SUN',  # Sunday 3 AM
        client=client
    )
```

---

## 🏢 PHASE 10: Enterprise Features (Weeks 57-68)

**Goal:** Enterprise-grade features for business use
**Dependencies:** Phase 4 (security), Phase 8 (analytics)
**Deliverables:** Multi-tenancy, SSO, RBAC, compliance

### 10.1 Multi-Tenancy Architecture (Week 57-60)

#### Tenant Isolation System
```python
# src/spotify_mcp/enterprise/multitenancy.py
from typing import Optional, Dict, List
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship

class Tenant(Base):
    """Organization/tenant model"""

    __tablename__ = 'tenants'

    id = Column(String(36), primary_key=True)
    name = Column(String(255), nullable=False)
    subdomain = Column(String(100), unique=True)
    plan = Column(String(50))  # free, pro, enterprise
    max_users = Column(Integer, default=10)
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Settings
    settings = Column(JSON)

    # Relationships
    users = relationship("TenantUser", back_populates="tenant")
    api_keys = relationship("TenantAPIKey", back_populates="tenant")

class TenantUser(Base):
    """User belonging to a tenant"""

    __tablename__ = 'tenant_users'

    id = Column(String(36), primary_key=True)
    tenant_id = Column(String(36), ForeignKey('tenants.id'))
    user_id = Column(String(100))  # Spotify user ID
    email = Column(String(255))
    role = Column(String(50))  # admin, user, readonly
    enabled = Column(Boolean, default=True)

    tenant = relationship("Tenant", back_populates="users")

class TenantManager:
    """Manage multi-tenant operations"""

    def __init__(self, db_session: Session):
        self.db = db_session

    async def create_tenant(
        self,
        name: str,
        subdomain: str,
        plan: str = "free"
    ) -> Tenant:
        """Create a new tenant"""

        tenant = Tenant(
            id=str(uuid.uuid4()),
            name=name,
            subdomain=subdomain,
            plan=plan,
            max_users=self._get_plan_limits(plan)['max_users']
        )

        self.db.add(tenant)
        await self.db.commit()

        # Create default admin API key
        await self._create_api_key(tenant.id, 'admin')

        return tenant

    async def add_user_to_tenant(
        self,
        tenant_id: str,
        user_id: str,
        email: str,
        role: str = "user"
    ) -> TenantUser:
        """Add user to tenant"""

        # Check user limit
        tenant = await self.get_tenant(tenant_id)
        user_count = await self.get_user_count(tenant_id)

        if user_count >= tenant.max_users:
            raise ValueError("Tenant user limit reached")

        user = TenantUser(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            user_id=user_id,
            email=email,
            role=role
        )

        self.db.add(user)
        await self.db.commit()

        return user

    def _get_plan_limits(self, plan: str) -> Dict:
        """Get limits for plan"""

        plans = {
            'free': {
                'max_users': 5,
                'max_api_calls_per_day': 1000,
                'features': ['basic']
            },
            'pro': {
                'max_users': 50,
                'max_api_calls_per_day': 50000,
                'features': ['basic', 'analytics', 'automation']
            },
            'enterprise': {
                'max_users': -1,  # Unlimited
                'max_api_calls_per_day': -1,
                'features': ['basic', 'analytics', 'automation', 'sso', 'audit']
            }
        }

        return plans.get(plan, plans['free'])

    async def get_tenant_by_subdomain(self, subdomain: str) -> Optional[Tenant]:
        """Get tenant by subdomain"""

        return self.db.query(Tenant).filter(
            Tenant.subdomain == subdomain,
            Tenant.enabled == True
        ).first()

    async def check_quota(self, tenant_id: str, quota_type: str) -> bool:
        """Check if tenant has quota remaining"""

        tenant = await self.get_tenant(tenant_id)
        limits = self._get_plan_limits(tenant.plan)

        if quota_type == 'api_calls':
            # Check daily API call limit
            today_calls = await self._get_today_api_calls(tenant_id)
            max_calls = limits['max_api_calls_per_day']

            return max_calls == -1 or today_calls < max_calls

        return True
```

### 10.2 Single Sign-On (SSO) Integration (Week 61-62)

#### SAML & OAuth SSO
```python
# src/spotify_mcp/enterprise/sso.py
from onelogin.saml2.auth import OneLogin_Saml2_Auth
from typing import Dict, Optional

class SSOProvider:
    """Base SSO provider"""

    async def authenticate(self, request_data: Dict) -> Optional[Dict]:
        """Authenticate user via SSO"""
        raise NotImplementedError

class SAMLProvider(SSOProvider):
    """SAML 2.0 SSO provider"""

    def __init__(self, settings: Dict):
        self.settings = settings

    async def authenticate(self, request_data: Dict) -> Optional[Dict]:
        """Authenticate via SAML"""

        auth = OneLogin_Saml2_Auth(request_data, self.settings)

        auth.process_response()

        if auth.is_authenticated():
            attributes = auth.get_attributes()

            return {
                'user_id': auth.get_nameid(),
                'email': attributes.get('email', [None])[0],
                'name': attributes.get('displayName', [None])[0],
                'groups': attributes.get('groups', [])
            }

        return None

    def get_login_url(self) -> str:
        """Get SSO login URL"""
        auth = OneLogin_Saml2_Auth({}, self.settings)
        return auth.login()

class OAuth2Provider(SSOProvider):
    """OAuth 2.0 SSO provider (Okta, Auth0, etc.)"""

    def __init__(self, client_id: str, client_secret: str, issuer: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.issuer = issuer

    async def authenticate(self, code: str) -> Optional[Dict]:
        """Exchange OAuth code for user info"""

        # Exchange code for token
        token_response = await self._exchange_code(code)

        # Get user info
        user_info = await self._get_user_info(token_response['access_token'])

        return {
            'user_id': user_info['sub'],
            'email': user_info['email'],
            'name': user_info['name']
        }

class SSOManager:
    """Manage SSO providers"""

    def __init__(self):
        self.providers = {}

    def register_provider(self, tenant_id: str, provider: SSOProvider):
        """Register SSO provider for tenant"""
        self.providers[tenant_id] = provider

    async def authenticate(self, tenant_id: str, auth_data: Dict) -> Optional[Dict]:
        """Authenticate user with tenant's SSO provider"""

        provider = self.providers.get(tenant_id)
        if not provider:
            return None

        return await provider.authenticate(auth_data)
```

### 10.3 Role-Based Access Control (RBAC) (Week 63-64)

#### RBAC System
```python
# src/spotify_mcp/enterprise/rbac.py
from enum import Enum
from typing import List, Set

class Permission(Enum):
    # Playback
    PLAYBACK_READ = "playback:read"
    PLAYBACK_CONTROL = "playback:control"

    # Library
    LIBRARY_READ = "library:read"
    LIBRARY_WRITE = "library:write"

    # Playlists
    PLAYLIST_READ = "playlist:read"
    PLAYLIST_CREATE = "playlist:create"
    PLAYLIST_MODIFY = "playlist:modify"
    PLAYLIST_DELETE = "playlist:delete"

    # Analytics
    ANALYTICS_VIEW = "analytics:view"
    ANALYTICS_EXPORT = "analytics:export"

    # Admin
    TENANT_MANAGE = "tenant:manage"
    USER_MANAGE = "user:manage"

class Role:
    """Role with permissions"""

    def __init__(self, name: str, permissions: List[Permission]):
        self.name = name
        self.permissions = set(permissions)

    def has_permission(self, permission: Permission) -> bool:
        return permission in self.permissions

# Predefined roles
ROLES = {
    'readonly': Role('readonly', [
        Permission.PLAYBACK_READ,
        Permission.LIBRARY_READ,
        Permission.PLAYLIST_READ,
        Permission.ANALYTICS_VIEW
    ]),

    'user': Role('user', [
        Permission.PLAYBACK_READ,
        Permission.PLAYBACK_CONTROL,
        Permission.LIBRARY_READ,
        Permission.LIBRARY_WRITE,
        Permission.PLAYLIST_READ,
        Permission.PLAYLIST_CREATE,
        Permission.PLAYLIST_MODIFY,
        Permission.ANALYTICS_VIEW
    ]),

    'admin': Role('admin', [
        # All permissions
        *list(Permission)
    ])
}

class RBACMiddleware:
    """Middleware to enforce RBAC"""

    def __init__(self):
        self.endpoint_permissions = self._build_permission_map()

    def _build_permission_map(self) -> Dict[str, Permission]:
        """Map endpoints to required permissions"""

        return {
            'GET /playback/state': Permission.PLAYBACK_READ,
            'POST /playback/play': Permission.PLAYBACK_CONTROL,
            'GET /library/tracks': Permission.LIBRARY_READ,
            'POST /library/tracks': Permission.LIBRARY_WRITE,
            'POST /playlists': Permission.PLAYLIST_CREATE,
            'DELETE /playlists/*': Permission.PLAYLIST_DELETE,
            'GET /analytics/*': Permission.ANALYTICS_VIEW,
        }

    async def check_permission(
        self,
        user_role: str,
        endpoint: str,
        method: str
    ) -> bool:
        """Check if user has permission for endpoint"""

        # Get required permission
        endpoint_key = f"{method} {endpoint}"
        required_permission = self.endpoint_permissions.get(endpoint_key)

        if not required_permission:
            return True  # No permission required

        # Get user's role
        role = ROLES.get(user_role)
        if not role:
            return False

        return role.has_permission(required_permission)
```

### 10.4 Compliance & Audit Logging (Week 65-68)

#### Comprehensive Audit System
```python
# src/spotify_mcp/enterprise/audit.py
from typing import Dict, Optional, List
from datetime import datetime

class AuditLog(Base):
    """Audit log entry"""

    __tablename__ = 'audit_logs'

    id = Column(String(36), primary_key=True)
    tenant_id = Column(String(36), ForeignKey('tenants.id'))
    user_id = Column(String(100))
    action = Column(String(100))
    resource_type = Column(String(50))
    resource_id = Column(String(100))
    changes = Column(JSON)
    ip_address = Column(String(50))
    user_agent = Column(String(500))
    timestamp = Column(DateTime, default=datetime.utcnow)
    status = Column(String(20))  # success, failure

class AuditLogger:
    """Enterprise audit logging"""

    def __init__(self, db_session: Session):
        self.db = db_session

    async def log(
        self,
        tenant_id: str,
        user_id: str,
        action: str,
        resource_type: str,
        resource_id: str,
        changes: Optional[Dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        status: str = "success"
    ):
        """Create audit log entry"""

        log_entry = AuditLog(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            changes=changes,
            ip_address=ip_address,
            user_agent=user_agent,
            status=status
        )

        self.db.add(log_entry)
        await self.db.commit()

    async def search_logs(
        self,
        tenant_id: str,
        filters: Optional[Dict] = None,
        limit: int = 100
    ) -> List[AuditLog]:
        """Search audit logs"""

        query = self.db.query(AuditLog).filter(
            AuditLog.tenant_id == tenant_id
        )

        if filters:
            if 'user_id' in filters:
                query = query.filter(AuditLog.user_id == filters['user_id'])

            if 'action' in filters:
                query = query.filter(AuditLog.action == filters['action'])

            if 'start_date' in filters:
                query = query.filter(AuditLog.timestamp >= filters['start_date'])

            if 'end_date' in filters:
                query = query.filter(AuditLog.timestamp <= filters['end_date'])

        return query.order_by(AuditLog.timestamp.desc()).limit(limit).all()

    async def generate_compliance_report(
        self,
        tenant_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict:
        """Generate compliance report"""

        logs = await self.search_logs(
            tenant_id,
            {'start_date': start_date, 'end_date': end_date},
            limit=10000
        )

        # Analyze logs
        total_actions = len(logs)
        failed_actions = sum(1 for log in logs if log.status == 'failure')
        unique_users = len(set(log.user_id for log in logs))

        # Action breakdown
        action_counts = {}
        for log in logs:
            action_counts[log.action] = action_counts.get(log.action, 0) + 1

        return {
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            },
            'summary': {
                'total_actions': total_actions,
                'failed_actions': failed_actions,
                'success_rate': (total_actions - failed_actions) / total_actions * 100,
                'unique_users': unique_users
            },
            'action_breakdown': action_counts,
            'detailed_logs': [self._format_log(log) for log in logs[:100]]
        }

    def _format_log(self, log: AuditLog) -> Dict:
        """Format log entry for export"""

        return {
            'timestamp': log.timestamp.isoformat(),
            'user': log.user_id,
            'action': log.action,
            'resource': f"{log.resource_type}/{log.resource_id}",
            'status': log.status,
            'ip_address': log.ip_address
        }
```

---

**Continue with final phases (11-15) covering Cloud, Real-Time, Plugins, and Launch?**

Should I:
1. ✅ Complete the final 5 phases
2. ✅ Create executive summary with timeline
3. ✅ Begin Phase 1 implementation now

Let me know!
