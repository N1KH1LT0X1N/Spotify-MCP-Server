# 🚀 Implementation Roadmap - Part 5: Cloud, Scale & Launch (FINAL)

## ☁️ PHASE 11: Cloud & Deployment (Weeks 69-76)

**Goal:** Production deployment infrastructure
**Dependencies:** All previous phases (complete system)
**Deliverables:** Cloud infrastructure, CI/CD, monitoring

### 11.1 Infrastructure as Code (Week 69-70)

#### Terraform Configuration
```hcl
# infrastructure/terraform/main.tf
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# VPC
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "spotify-mcp-vpc"
  }
}

# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "spotify-mcp-cluster"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

# ECS Task Definition
resource "aws_ecs_task_definition" "app" {
  family                   = "spotify-mcp-server"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.fargate_cpu
  memory                   = var.fargate_memory
  execution_role_arn       = aws_iam_role.ecs_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([{
    name  = "spotify-mcp-server"
    image = "${var.ecr_repository_url}:${var.image_tag}"

    portMappings = [{
      containerPort = 8000
      protocol      = "tcp"
    }]

    environment = [
      {
        name  = "ENVIRONMENT"
        value = var.environment
      },
      {
        name  = "CACHE_BACKEND"
        value = "redis"
      },
      {
        name  = "CACHE_REDIS_URL"
        value = "redis://${aws_elasticache_cluster.redis.cache_nodes.0.address}:6379"
      }
    ]

    secrets = [
      {
        name      = "SPOTIFY_CLIENT_ID"
        valueFrom = "${aws_secretsmanager_secret.spotify_credentials.arn}:client_id::"
      },
      {
        name      = "SPOTIFY_CLIENT_SECRET"
        valueFrom = "${aws_secretsmanager_secret.spotify_credentials.arn}:client_secret::"
      }
    ]

    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = aws_cloudwatch_log_group.app.name
        "awslogs-region"        = var.aws_region
        "awslogs-stream-prefix" = "ecs"
      }
    }

    healthCheck = {
      command     = ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"]
      interval    = 30
      timeout     = 5
      retries     = 3
      startPeriod = 60
    }
  }])
}

# Application Load Balancer
resource "aws_lb" "main" {
  name               = "spotify-mcp-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = aws_subnet.public.*.id

  enable_deletion_protection = var.environment == "prod" ? true : false
}

# RDS PostgreSQL Database
resource "aws_db_instance" "postgres" {
  identifier             = "spotify-mcp-db"
  engine                 = "postgres"
  engine_version         = "15.4"
  instance_class         = var.db_instance_class
  allocated_storage      = var.db_allocated_storage
  storage_encrypted      = true
  db_name                = "spotify_mcp"
  username               = var.db_username
  password               = var.db_password
  vpc_security_group_ids = [aws_security_group.db.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name
  multi_az               = var.environment == "prod" ? true : false
  backup_retention_period = 7
  skip_final_snapshot    = var.environment != "prod"

  tags = {
    Name = "spotify-mcp-db"
  }
}

# ElastiCache Redis
resource "aws_elasticache_cluster" "redis" {
  cluster_id           = "spotify-mcp-cache"
  engine               = "redis"
  engine_version       = "7.0"
  node_type            = var.redis_node_type
  num_cache_nodes      = 1
  parameter_group_name = "default.redis7"
  port                 = 6379
  security_group_ids   = [aws_security_group.redis.id]
  subnet_group_name    = aws_elasticache_subnet_group.main.name

  tags = {
    Name = "spotify-mcp-cache"
  }
}

# Auto Scaling
resource "aws_appautoscaling_target" "ecs" {
  max_capacity       = 10
  min_capacity       = 2
  resource_id        = "service/${aws_ecs_cluster.main.name}/${aws_ecs_service.main.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

resource "aws_appautoscaling_policy" "ecs_cpu" {
  name               = "cpu-autoscaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.ecs.resource_id
  scalable_dimension = aws_appautoscaling_target.ecs.scalable_dimension
  service_namespace  = aws_appautoscaling_target.ecs.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
    target_value = 70.0
  }
}

# CloudFront CDN
resource "aws_cloudfront_distribution" "main" {
  origin {
    domain_name = aws_lb.main.dns_name
    origin_id   = "alb"

    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "https-only"
      origin_ssl_protocols   = ["TLSv1.2"]
    }
  }

  enabled             = true
  is_ipv6_enabled     = true
  comment             = "Spotify MCP Server CDN"
  default_root_object = ""

  default_cache_behavior {
    allowed_methods  = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "alb"

    forwarded_values {
      query_string = true
      headers      = ["Authorization", "Host"]

      cookies {
        forward = "all"
      }
    }

    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 3600
    max_ttl                = 86400
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    acm_certificate_arn = aws_acm_certificate.main.arn
    ssl_support_method  = "sni-only"
  }
}
```

#### Kubernetes (Alternative)
```yaml
# infrastructure/kubernetes/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: spotify-mcp-server
  namespace: production
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: spotify-mcp-server
  template:
    metadata:
      labels:
        app: spotify-mcp-server
        version: v1.0.4
    spec:
      containers:
      - name: server
        image: your-registry/spotify-mcp-server:latest
        ports:
        - containerPort: 8000
          name: http
        env:
        - name: ENVIRONMENT
          value: "production"
        - name: CACHE_BACKEND
          value: "redis"
        - name: CACHE_REDIS_URL
          valueFrom:
            secretKeyRef:
              name: redis-credentials
              key: url
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: postgres-credentials
              key: url
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5

---
apiVersion: v1
kind: Service
metadata:
  name: spotify-mcp-service
  namespace: production
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 8000
    protocol: TCP
  selector:
    app: spotify-mcp-server

---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: spotify-mcp-hpa
  namespace: production
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: spotify-mcp-server
  minReplicas: 3
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### 11.2 Advanced CI/CD Pipeline (Week 71-72)

#### GitHub Actions - Production Pipeline
```yaml
# .github/workflows/production-deploy.yml
name: Production Deployment

on:
  push:
    tags:
      - 'v*'

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run comprehensive tests
        run: |
          pytest --cov --cov-fail-under=90
          pytest tests/integration/ --slow
          pytest tests/load/ --benchmark

  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          exit-code: '1'
          severity: 'CRITICAL,HIGH'

      - name: SAST with Semgrep
        uses: returntocorp/semgrep-action@v1

  build-and-push:
    needs: [test, security-scan]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1

      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v1

      - name: Build, tag, and push image
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          ECR_REPOSITORY: spotify-mcp-server
          IMAGE_TAG: ${{ github.ref_name }}
        run: |
          docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG .
          docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:latest .
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:latest

  deploy-staging:
    needs: build-and-push
    runs-on: ubuntu-latest
    environment: staging
    steps:
      - name: Deploy to staging
        run: |
          terraform init
          terraform workspace select staging
          terraform apply -auto-approve

      - name: Run smoke tests
        run: |
          pytest tests/smoke/ --env=staging

  deploy-production:
    needs: deploy-staging
    runs-on: ubuntu-latest
    environment: production
    steps:
      - name: Blue-Green Deployment
        run: |
          # Deploy to green environment
          terraform apply -var="target_env=green" -auto-approve

          # Run health checks
          ./scripts/health-check.sh green

          # Switch traffic to green
          ./scripts/switch-traffic.sh green

          # Monitor for 10 minutes
          sleep 600

          # If healthy, destroy blue
          ./scripts/destroy-old-environment.sh blue

      - name: Rollback on failure
        if: failure()
        run: |
          ./scripts/rollback.sh

      - name: Notify Slack
        uses: slackapi/slack-github-action@v1.24.0
        with:
          payload: |
            {
              "text": "Production deployment ${{ job.status }}: ${{ github.ref_name }}"
            }
```

### 11.3 Database Migration Strategy (Week 73)

#### Zero-Downtime Migrations
```python
# src/spotify_mcp/database/migrations/migration_manager.py
from alembic import command
from alembic.config import Config
from typing import List

class MigrationManager:
    """Manage database migrations with zero downtime"""

    def __init__(self, db_url: str):
        self.alembic_cfg = Config("alembic.ini")
        self.alembic_cfg.set_main_option("sqlalchemy.url", db_url)

    async def apply_migrations(self, target: str = "head"):
        """Apply migrations with safety checks"""

        # 1. Backup database
        await self._backup_database()

        # 2. Check migration safety
        migrations = await self._get_pending_migrations()
        for migration in migrations:
            await self._validate_migration_safety(migration)

        # 3. Apply migrations
        command.upgrade(self.alembic_cfg, target)

        # 4. Verify data integrity
        await self._verify_data_integrity()

    async def _validate_migration_safety(self, migration):
        """Ensure migration won't cause downtime"""

        # Check for dangerous operations
        dangerous_ops = [
            'DROP TABLE',
            'DROP COLUMN',
            'ALTER COLUMN TYPE'  # Without USING clause
        ]

        migration_sql = migration.get_sql()

        for op in dangerous_ops:
            if op in migration_sql.upper():
                raise ValueError(f"Dangerous operation detected: {op}")

    async def rollback(self, steps: int = 1):
        """Rollback migrations"""

        # Restore from backup
        await self._restore_from_backup()

        command.downgrade(self.alembic_cfg, f"-{steps}")
```

### 11.4 Monitoring & Alerting Setup (Week 74-76)

#### Production Monitoring Stack
```yaml
# infrastructure/monitoring/prometheus-config.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

alerting:
  alertmanagers:
    - static_configs:
        - targets: ['alertmanager:9093']

rule_files:
  - "alerts/*.yml"

scrape_configs:
  - job_name: 'spotify-mcp-server'
    static_configs:
      - targets: ['spotify-mcp:8000']
    metrics_path: '/metrics'

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']

  - job_name: 'node'
    static_configs:
      - targets: ['node-exporter:9100']
```

```yaml
# infrastructure/monitoring/alerts/critical.yml
groups:
  - name: critical_alerts
    interval: 30s
    rules:
      # Service down
      - alert: ServiceDown
        expr: up{job="spotify-mcp-server"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Service is down"
          description: "{{ $labels.instance }} is down"

      # High error rate
      - alert: HighErrorRate
        expr: |
          rate(http_requests_total{status=~"5.."}[5m]) /
          rate(http_requests_total[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"

      # Database connection issues
      - alert: DatabaseConnectionsFull
        expr: |
          pg_stat_activity_count /
          pg_settings_max_connections > 0.9
        for: 5m
        labels:
          severity: warning

      # Cache degraded
      - alert: RedisDown
        expr: up{job="redis"} == 0
        for: 1m
        labels:
          severity: critical
```

---

## 🌐 PHASE 12: Real-Time & WebSocket Support (Weeks 77-84)

**Goal:** Real-time features for live collaboration
**Dependencies:** Phase 11 (infrastructure)
**Deliverables:** WebSocket server, pub/sub system

### 12.1 WebSocket Server (Week 77-79)

#### WebSocket Implementation
```python
# src/spotify_mcp/realtime/websocket_server.py
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Set, List
import asyncio
import json

class ConnectionManager:
    """Manage WebSocket connections"""

    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.user_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        """Accept new WebSocket connection"""
        await websocket.accept()
        self.user_connections[user_id] = websocket

        # Add to user's room
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)

    def disconnect(self, websocket: WebSocket, user_id: str):
        """Remove WebSocket connection"""
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

        if user_id in self.user_connections:
            del self.user_connections[user_id]

    async def send_personal_message(self, message: dict, user_id: str):
        """Send message to specific user"""
        if user_id in self.user_connections:
            websocket = self.user_connections[user_id]
            await websocket.send_json(message)

    async def broadcast(self, message: dict, room: str = None):
        """Broadcast message to all connections in room"""
        connections = self.active_connections.get(room, set())

        for connection in connections:
            try:
                await connection.send_json(message)
            except Exception:
                pass  # Connection already closed

manager = ConnectionManager()

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """WebSocket endpoint for real-time updates"""

    await manager.connect(websocket, user_id)

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()

            # Handle different message types
            message_type = data.get('type')

            if message_type == 'subscribe_playback':
                # Subscribe to playback updates
                await subscribe_to_playback_updates(user_id)

            elif message_type == 'subscribe_playlist':
                # Subscribe to playlist changes
                playlist_id = data.get('playlist_id')
                await subscribe_to_playlist(user_id, playlist_id)

            elif message_type == 'ping':
                # Heartbeat
                await manager.send_personal_message(
                    {'type': 'pong', 'timestamp': time.time()},
                    user_id
                )

    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)

async def subscribe_to_playback_updates(user_id: str):
    """Stream playback state changes"""

    while True:
        # Get current playback state
        state = await spotify_client.current_playback()

        # Send update
        await manager.send_personal_message({
            'type': 'playback_update',
            'data': state
        }, user_id)

        # Wait before next update
        await asyncio.sleep(2)  # Update every 2 seconds
```

### 12.2 Pub/Sub System (Week 80-81)

#### Redis Pub/Sub for Events
```python
# src/spotify_mcp/realtime/pubsub.py
import redis.asyncio as redis
import json
from typing import Callable, Dict

class PubSubManager:
    """Redis-based pub/sub for real-time events"""

    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url)
        self.pubsub = self.redis.pubsub()
        self.handlers: Dict[str, Callable] = {}

    async def publish(self, channel: str, message: dict):
        """Publish message to channel"""
        await self.redis.publish(
            channel,
            json.dumps(message)
        )

    async def subscribe(self, channel: str, handler: Callable):
        """Subscribe to channel"""
        await self.pubsub.subscribe(channel)
        self.handlers[channel] = handler

    async def listen(self):
        """Listen for messages"""
        async for message in self.pubsub.listen():
            if message['type'] == 'message':
                channel = message['channel'].decode()
                data = json.loads(message['data'].decode())

                # Call handler
                handler = self.handlers.get(channel)
                if handler:
                    await handler(data)

# Event types
class SpotifyEvents:
    TRACK_PLAYED = "spotify:track:played"
    TRACK_LIKED = "spotify:track:liked"
    PLAYLIST_UPDATED = "spotify:playlist:updated"
    PLAYBACK_STATE_CHANGED = "spotify:playback:changed"

# Usage
pubsub = PubSubManager(redis_url="redis://localhost")

# Publish events
await pubsub.publish(SpotifyEvents.TRACK_PLAYED, {
    'user_id': 'user123',
    'track_id': 'track456',
    'timestamp': time.time()
})

# Subscribe to events
async def handle_track_played(data: dict):
    user_id = data['user_id']
    track_id = data['track_id']

    # Send WebSocket notification
    await manager.send_personal_message({
        'type': 'track_played',
        'track_id': track_id
    }, user_id)

await pubsub.subscribe(SpotifyEvents.TRACK_PLAYED, handle_track_played)
```

### 12.3 Collaborative Features (Week 82-84)

#### Real-Time Collaborative Playlists
```python
# src/spotify_mcp/realtime/collaboration.py
from typing import List, Set
import asyncio

class CollaborativePlaylist:
    """Real-time collaborative playlist editing"""

    def __init__(self, playlist_id: str, pubsub: PubSubManager):
        self.playlist_id = playlist_id
        self.pubsub = pubsub
        self.active_users: Set[str] = set()
        self.lock = asyncio.Lock()

    async def join(self, user_id: str):
        """User joins collaborative session"""
        async with self.lock:
            self.active_users.add(user_id)

            # Notify other users
            await self.pubsub.publish(
                f"playlist:{self.playlist_id}",
                {
                    'type': 'user_joined',
                    'user_id': user_id,
                    'active_users': list(self.active_users)
                }
            )

    async def add_track(self, user_id: str, track_uri: str):
        """Add track with real-time sync"""

        # Add to Spotify
        await spotify_client.add_tracks_to_playlist(
            self.playlist_id,
            [track_uri]
        )

        # Broadcast change
        await self.pubsub.publish(
            f"playlist:{self.playlist_id}",
            {
                'type': 'track_added',
                'user_id': user_id,
                'track_uri': track_uri,
                'timestamp': time.time()
            }
        )

    async def reorder_tracks(self, user_id: str, new_order: List[int]):
        """Reorder tracks with conflict resolution"""

        async with self.lock:
            # Apply reordering
            await spotify_client.reorder_playlist_items(
                self.playlist_id,
                range_start=0,
                insert_before=0,
                range_length=len(new_order),
                snapshot_id=None
            )

            # Broadcast
            await self.pubsub.publish(
                f"playlist:{self.playlist_id}",
                {
                    'type': 'tracks_reordered',
                    'user_id': user_id,
                    'new_order': new_order
                }
            )
```

---

## 🔌 PHASE 13: Plugin Architecture & Marketplace (Weeks 85-96)

**Goal:** Extensible plugin system
**Dependencies:** All core features complete
**Deliverables:** Plugin SDK, marketplace, sample plugins

### 13.1 Plugin SDK (Week 85-88)

#### Plugin System Architecture
```python
# src/spotify_mcp/plugins/plugin_sdk.py
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import importlib
import inspect

class PluginHook(Enum):
    """Available plugin hooks"""
    ON_TRACK_PLAY = "on_track_play"
    ON_TRACK_END = "on_track_end"
    ON_PLAYLIST_CREATE = "on_playlist_create"
    ON_SEARCH = "on_search"
    BEFORE_PLAY = "before_play"
    AFTER_PLAY = "after_play"

class Plugin(ABC):
    """Base plugin class"""

    @property
    @abstractmethod
    def name(self) -> str:
        """Plugin name"""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """Plugin version"""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Plugin description"""
        pass

    @property
    def hooks(self) -> List[PluginHook]:
        """Hooks this plugin listens to"""
        return []

    async def on_enable(self):
        """Called when plugin is enabled"""
        pass

    async def on_disable(self):
        """Called when plugin is disabled"""
        pass

    async def handle_hook(self, hook: PluginHook, data: Dict[str, Any]) -> Optional[Dict]:
        """Handle a hook event"""
        method_name = f"_{hook.value}"
        if hasattr(self, method_name):
            return await getattr(self, method_name)(data)
        return None

class PluginManager:
    """Manage plugins"""

    def __init__(self):
        self.plugins: Dict[str, Plugin] = {}
        self.hooks: Dict[PluginHook, List[Plugin]] = {hook: [] for hook in PluginHook}

    def register_plugin(self, plugin: Plugin):
        """Register a plugin"""
        self.plugins[plugin.name] = plugin

        # Register hooks
        for hook in plugin.hooks:
            self.hooks[hook].append(plugin)

    async def trigger_hook(self, hook: PluginHook, data: Dict[str, Any]) -> List[Any]:
        """Trigger a hook and collect responses"""
        results = []

        for plugin in self.hooks.get(hook, []):
            try:
                result = await plugin.handle_hook(hook, data)
                if result:
                    results.append(result)
            except Exception as e:
                logger.error(f"Plugin {plugin.name} error on hook {hook}: {e}")

        return results

    def load_plugin_from_file(self, filepath: str):
        """Dynamically load plugin from file"""
        spec = importlib.util.spec_from_file_location("plugin", filepath)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Find Plugin subclass
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and issubclass(obj, Plugin) and obj != Plugin:
                plugin_instance = obj()
                self.register_plugin(plugin_instance)
                return plugin_instance

        raise ValueError("No Plugin class found in file")

# Global plugin manager
plugin_manager = PluginManager()

# Example plugin
class LastFMScrobblerPlugin(Plugin):
    """Last.fm scrobbling plugin"""

    name = "lastfm-scrobbler"
    version = "1.0.0"
    description = "Scrobble tracks to Last.fm"

    def __init__(self, api_key: str, session_key: str):
        self.api_key = api_key
        self.session_key = session_key
        self.hooks = [PluginHook.ON_TRACK_PLAY]

    async def _on_track_play(self, data: Dict) -> None:
        """Scrobble track when played"""
        track = data['track']

        # Scrobble to Last.fm
        await self._scrobble(
            artist=track['artists'][0]['name'],
            track=track['name'],
            timestamp=int(time.time())
        )

    async def _scrobble(self, artist: str, track: str, timestamp: int):
        """Call Last.fm API"""
        # Implementation
        pass
```

### 13.2 Plugin Marketplace (Week 89-92)

#### Marketplace Backend
```python
# src/spotify_mcp/marketplace/marketplace.py
from typing import List, Optional
from pydantic import BaseModel

class PluginListing(BaseModel):
    id: str
    name: str
    description: str
    version: str
    author: str
    category: str
    downloads: int
    rating: float
    verified: bool
    source_url: str
    documentation_url: Optional[str]
    price: float  # 0 for free
    screenshots: List[str]
    dependencies: List[str]

class MarketplaceAPI:
    """Plugin marketplace API"""

    def __init__(self, db_session):
        self.db = db_session

    async def list_plugins(
        self,
        category: Optional[str] = None,
        search: Optional[str] = None,
        sort_by: str = "downloads"
    ) -> List[PluginListing]:
        """List available plugins"""

        query = self.db.query(PluginListing)

        if category:
            query = query.filter(PluginListing.category == category)

        if search:
            query = query.filter(
                PluginListing.name.contains(search) |
                PluginListing.description.contains(search)
            )

        if sort_by == "downloads":
            query = query.order_by(PluginListing.downloads.desc())
        elif sort_by == "rating":
            query = query.order_by(PluginListing.rating.desc())
        elif sort_by == "recent":
            query = query.order_by(PluginListing.created_at.desc())

        return query.all()

    async def install_plugin(self, plugin_id: str, user_id: str):
        """Install plugin for user"""

        # Download plugin package
        plugin_package = await self._download_plugin(plugin_id)

        # Verify signature
        await self._verify_plugin_signature(plugin_package)

        # Install to user's plugins directory
        plugin_path = f"/plugins/{user_id}/{plugin_id}"
        await self._extract_plugin(plugin_package, plugin_path)

        # Load plugin
        plugin = plugin_manager.load_plugin_from_file(f"{plugin_path}/main.py")

        # Enable for user
        await plugin.on_enable()

        # Track installation
        await self._track_installation(plugin_id, user_id)

    async def publish_plugin(
        self,
        author_id: str,
        plugin_data: Dict
    ) -> PluginListing:
        """Publish new plugin to marketplace"""

        # Validate plugin
        await self._validate_plugin(plugin_data)

        # Create listing
        listing = PluginListing(
            id=str(uuid.uuid4()),
            **plugin_data,
            author=author_id,
            downloads=0,
            rating=0.0,
            verified=False  # Requires manual review
        )

        self.db.add(listing)
        await self.db.commit()

        # Queue for review
        await self._queue_for_review(listing.id)

        return listing
```

### 13.3 Sample Official Plugins (Week 93-96)

#### Lyrics Plugin
```python
# plugins/official/lyrics/main.py
from spotify_mcp.plugins import Plugin, PluginHook
import lyricsgenius

class LyricsPlugin(Plugin):
    """Display lyrics for playing track"""

    name = "lyrics-display"
    version = "1.0.0"
    description = "Show lyrics for currently playing track"
    hooks = [PluginHook.ON_TRACK_PLAY]

    def __init__(self, genius_api_key: str):
        self.genius = lyricsgenius.Genius(genius_api_key)

    async def _on_track_play(self, data: Dict) -> Dict:
        """Fetch and return lyrics"""
        track = data['track']

        # Search for lyrics
        song = self.genius.search_song(
            track['name'],
            track['artists'][0]['name']
        )

        return {
            'lyrics': song.lyrics if song else None,
            'source': 'genius'
        }
```

#### Concert Finder Plugin
```python
# plugins/official/concerts/main.py
class ConcertFinderPlugin(Plugin):
    """Find concerts for artists you listen to"""

    name = "concert-finder"
    version = "1.0.0"
    description = "Get notified of concerts by your favorite artists"
    hooks = [PluginHook.ON_TRACK_PLAY]

    def __init__(self, songkick_api_key: str):
        self.api_key = songkick_api_key

    async def _on_track_play(self, data: Dict) -> Optional[Dict]:
        """Check for upcoming concerts"""
        artist = data['track']['artists'][0]['name']

        # Search Songkick
        concerts = await self._search_concerts(artist)

        if concerts:
            return {
                'artist': artist,
                'upcoming_concerts': concerts,
                'notification': f"{len(concerts)} upcoming concerts for {artist}"
            }

        return None
```

---

**Continue with final phases 14-15 and executive summary?**

Let me know if you want me to:
1. ✅ Complete final 2 phases (Advanced Features & Launch)
2. ✅ Create executive summary with prioritized action plan
3. ✅ Start implementing Phase 1 immediately

What's next?
