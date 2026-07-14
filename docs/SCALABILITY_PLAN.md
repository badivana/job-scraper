# Scalability Plan

## Purpose

To outline how the AI‑Powered Job Finder system scales to accommodate growth in users, job volume, and traffic while maintaining performance, reliability, and cost efficiency. The plan covers horizontal scaling, database strategies, caching, asynchronous processing, and observability.

## Contents

- Growth Expectations
- Scaling Principles
- Frontend Scaling
- Backend Scaling
- Database Scaling
- Caching Strategy
- Asynchronous Processing & Worker Scaling
- Network & Edge Considerations
- Observability-Driven Scaling
- Cost Optimization
- Bottleneck Analysis & Mitigation
- Scaling Triggers & Automation
- Future-Proofing

## Growth Expectations (Baseline Assumptions)

| Metric | Target ( Year 1 ) | Target ( Year 2 ) | Target ( Year 3 ) |
|--------|-------------------|-------------------|-------------------|
| Monthly Active Users (MAU) | 50 k | 250 k | 1 M |
| Daily Active Users (DAU) | 15 k | 75 k | 300 k |
| Jobs stored (raw+cleaned) | 5 M | 25 M | 80 M |
| Concurrent API requests (peak) | 200 | 1 000 | 5 000 |
| Resume uploads per day | 1 k | 5 k | 20 k |
| AI generation requests per day | 2 k | 10 k | 40 k |
| Email sends per day | 10 k | 50 k | 200 k |
| Data ingest rate (jobs/day) | 50 k | 250 k | 1 M |

These numbers inform the sizing of each layer; the plan is designed to handle at least an order of magnitude above the Year‑3 targets.

## Scaling Principles

1. **Horizontal First** – Prefer adding more instances over upgrading a single node (vertical scaling) wherever possible.
2. **Stateless Services** – Keep backend and frontend instances stateless; store session data in Redis or JWT.
3. **Database Read Replicas** – Offload read‑heavy workloads (job search, matching, analytics) to replicas.
4. **Sharding by Tenant/Geo** – If needed, split data by geographic region or user‑ID hash to distribute load.
5. **Event‑Driven & Queues** – Use Celery + Redis for burstable workloads (scraping, AI generation, email).
6. **Cache‑Aside** – Frequently accessed data (user profiles, recent jobs, top matches) cached in Redis with TTL.
7. **Observable Scaling** – Scale based on metrics (CPU, latency, queue length, error rates) rather than heuristics.
8. **Gradual Rollout** – Use feature flags and canary deployments to validate scaling changes under real traffic.
9. **Data Lifecycle** – Archive or delete stale data (raw scraped JSON >30 days, jobs >90 days inactive) to keep hot set small.
10. **Multi‑Region Readiness** – Design for active‑active or active‑passive deployment across regions to reduce latency and provide disaster recovery.

## Frontend Scaling

- **Static Site Hosting**: The Next.js app can be exported as static (if SSR not required) and served via a CDN (Cloudflare, Vercel, Netlify) – essentially infinite scalability for static assets.
- **Server‑Side Rendering (SSR)**: If SSR is needed for personalised pages, deploy the Next.js server in containers behind an autoscaling group or managed service (e.g., AWS Fargate, Google Cloud Run, Azure Container Apps). Scale based on CPU utilization and request rate (target 70 % CPU, p95 latency < 800 ms).
- **Edge Functions**: Offload non‑personalised logic (e.g., public landing pages, SEO metadata) to edge workers (Cloudflare Workers, Vercel Edge Functions) to reduce origin load.
- **Asset Optimization**: Use `next/image` with responsive breakpoints and modern formats (WebP/AVIF) to minimize bytes transferred.
- **Cache Control**: Set appropriate `Cache‑Control` headers (`public, max-age=31536000, immutable` for versioned assets; `stale-while-revalidate` for API responses that can be stale briefly).
- **CDN for API**: If using a global API gateway (e.g., AWS API Gateway with regional endpoints, or Cloudflare Workers as a reverse proxy), cache GET responses that are idempotent (public job listings, popular searches) with short TTL (10‑60 s).
- **Batching**: Combine multiple API calls into a single request where feasible (e.g., fetch multiple job details in one call) to reduce round trips.
- **Service Workers**: Implement offline‑capable caching for shell and critical resources (Workbox) to improve perceived performance under flaky connections.

## Backend Scaling

### Stateless API Instances

- Run multiple replicas of the FastAPI application behind a load balancer (NGINX, HAProxy, cloud LB, or Kubernetes Service).
- Each replica:
  - Connects to the same PostgreSQL (primary for writes, read replicas for reads).
  - Shares the same Redis cluster for caching and Celery broker.
  - Does not store local session state.
- **Autoscaling Triggers**:
  - CPU utilization > 70 % (average over 2 min) → add replica.
  - CPU utilization < 30 % (over 5 min) → remove replica (min 2).
  - Custom metric: request latency (p95) > 800 ms for 3 min → add replica.
  - Custom metric: error rate (5xx) > 2 % over 5 min → add replica (to handle overload).
- **Maximum Pods**: Define an upper bound (e.g., 20 replicas) to prevent runaway scaling; use horizontal pod autoscaler (HPA) in Kubernetes or equivalent in ECS/App Runner.

### Connection Pooling

- Use `asyncpg` pool with `size=20`, `max_overflow=10` per instance.
- Monitor pool usage (`pg_stat_activity`) to avoid exhaustion.
- If using PgBouncer (transaction pooling) in front of PostgreSQL, can reduce connection count.

### CPU vs I/O Bound

- The backend is largely I/O bound (database and I/O network (calls to Apify, OpenAI, Redis). Therefore, adding more instances often yields linear throughput gains until the database or external APIs become bottlenecks.
- For CPU‑bound tasks (e.g., heavy data transformations, image processing), consider offloading to separate worker pools or using `run_in_executor` with a limited process pool.

## Database Scaling

### Primary Write Handling

- The primary Supabase PostgreSQL instance receives all write operations (job inserts, resume inserts, application updates, etc.).
- Supabase offers vertical scaling (increase compute resources) as a first line of defense.
- For write‑heavy loads (> 5k writes/sec) consider:
  - **Partitioning** by time (monthly partitions on `jobs.posted_date`) to reduce index size and improve insert speed.
  - **Batch inserts** using `INSERT … VALUES … , … , …` (up to few hundred rows per statement) to reduce round trips.
  - **Asynchronous writes** via Celery (job ingestion, resume processing) to smooth bursts.

### Read Scaling

- **Read Replicas**: Supabase provides read‑only replicas (available on higher plans). Direct read‑heavy endpoints (job search, matching, analytics, dashboard) to the replica endpoint.
  - Use a router in the service layer that selects `READ_REPLICA_URL` for `SELECT` queries, and `PRIMARY_URL` for `INSERT/UPDATE/DELETE`.
  - Ensure applications tolerate eventual consistency (replica lag typically < 1 s for moderate load).
- **Connection Pooling to Replicas**: Same as primary but separate pool.
- **Read‑Only Routing Library**: Use `sqlalchemy` `engine` with `execution_options(isolation_level="READ COMMITTED")` and custom connect args.

### Indexing Strategy for Scale

- **Primary Keys**: UUID – random distribution leads to page splits; consider using `uuid-ossp` version 4; impact minimal for ≤ 100 M rows.
- **Indexes**:
  - `btree` on `posted_date` (BRIN alternative for large tables).
  - `gin` on `location` (JSONB) for geographic filters.
  - `gin` on `skills_array` (if storing as array).
  - `ivfflat` on `vector(1536)` (embedding) – monitor `lists` parameter; increase as data grows (rule of thumb: `lists = sqrt(num_vectors)/4`).
    - Example: 1M vectors → `lists ≈ 250`. Rebuild index nightly or weekly.
  - Consider `hsnsw` (if available) for higher recall with less memory.
- **Partitioned Indexes**: Build indexes on each partition individually to keep them small.

### Caching Layers to Reduce DB Load

- **Redis Cache**:
  - Cache recent job lists (e.g., "trending last 24h") with TTL 10 min.
  - Cache user profile + preferences (TTL 1 h) – fetched on login and updated on change.
  - Cache top‑N matches per user (TTL 5 min) – updated on resume upload or new job insert.
  - Cache API responses for idempotent, low‑change data (e.g., list of industries, contract types) with TTL 12 h.
- **Cache Invalidation**:
  - Use Redis pub/sub channels (`job_new`, `resume_updated`, `profile_updated`) to purge related keys.
  - Or adopt a "write‑through" pattern: on update, update both DB and cache.
- **Cache Warming**: On deployment, pre‑load hot lists (e.g., popular searches) to avoid cache stampede.

### Read‑Only Analytics

- Offload heavy analytical queries (e.g., daily aggregates, cohort analysis) to a separate read‑only replica or a data warehouse (Snowflake, BigQuery, Redshift) via periodic `COPY` or `pg_dump`/`pg_restore` or using `dblink`/`fdw`.
- Use materialized views refreshed nightly for metrics like "jobs per day by source".

## Caching Strategy

- **Layer 1 – HTTP/CDN Cache**: For static assets and idempotent GET API responses (public endpoints). Use `Cache-Control: public, max-age=86400, stale-while-revalidate=86400`.
- **Layer 2 – Application‑Level Redis Cache**: As detailed above, with specific TTLs and invalidation via pub/sub.
- **Layer 3 – Local Process Cache**: Use `functools.lru_cache` on pure functions that are expensive and deterministic (e.g., skill normalization lookup tables) – size limited to a few thousand entries.
- **Cache Sizing**:
  - Estimate Redis memory usage: aim for < 60 % utilization to allow headroom for bursts.
  - Monitor `used_memory`, `evicted_keys`, `hitrate`.
- **Eviction Policy**: `allkeys-lru` (default) works well for mixed workloads.
- **Monitoring**:
  - Track `keyspace_hits`, `keyspace_misses`, `total_commands_processed`.
  - Set alerts on low hit rate (< 80 %) or high eviction rate.

## Asynchronous Processing & Worker Scaling

### Worker Types

| Worker Queue | Purpose | Typical Load | Scaling Approach |
|--------------|---------|--------------|------------------|
| `job_ingest` | Fetch Apify results, normalize, dedup, store raw/cleaned | Burst‑driven (based on schedule) | Scale based on queue length (`llen job_ingest`) via KEDA or custom autoscaler |
| `resume_parse` | Uploaded resume → text extraction → sectioning → skill embedding → store | Correlates with user upload spikes | Scale based on `resume_parse` queue length |
| `embedding_batch` | Periodic recompute of stale embeddings (jobs/resumes) | Nightly/weekly batch | Fixed size (e.g., 2‑4 workers); can be scaled up if backlog grows |
| `notification_send` | Email dispatch via SMTP/API | Proportional to user actions (new matches, status changes) | Scale based on notification queue length |
| `maintenance` | Index rebuild, log cleanup, temp file prune | Low frequency, periodic | Single worker or schedule via cron |

### Autoscaling Workers (KEDA Example)

- Use **KEDA** (Kubernetes Event‑Driven Autoscaling) to scale based on Redis queue length:
  - `ScaledObject` triggers when `llen queue_name > threshold`.
  - Define `minReplicas=0`, `maxReplicas=20`, `pollingInterval=30s`.
- For non‑K8s environments (ECS, Cloud Run, VMs), implement a custom scaler that:
  - Periodically checks queue length (`redis.llen`).
  - Adjusts the desired number of worker instances via the cloud provider’s API (e.g., AWS Auto Scaling groups, Azure Scale Sets, GCP Managed Instance Groups).
- **Worker Instance Size**: Choose a size with adequate CPU and memory for the task (e.g., 2 vCPU, 4 GB RAM for ingestion; 1 vCPU, 2 GB for lightweight email sending).
- **Graceful Shutdown**: Workers should finish current task before shutting down (listen for `SIGTERM`, drain queue, acknowledge active tasks).

### Back‑Pressure & Rate Limiting

- External APIs (Apify, OpenAI) have rate limits; workers must respect them.
  - Use token‑bucket algorithm (`ratelimit` library) per worker or shared via Redis.
  - Log 429 responses and back off exponentially.
- Internal queue consumers should not flood the database; use batch inserts and consider `SELECT … FOR UPDATE SKIP LOCKED` for parallel processing of distinct rows.

## Network & Edge Considerations

- **Content Delivery Network (CDN)**:
  - Serve static assets (JS, CSS, images, fonts) from a CDN with edge locations close to users.
  - Enable HTTP/2 or HTTP/3 for better multiplexing.
  - Set appropriate `Cache-Control` headers for long‑term assets.
- **DNS**:
  - Use a low‑TTL (`300s`) for failover scenarios; higher TTL (`3600s`) for stable records.
  - Consider using a managed DNS service with health checks and traffic steering (Route 53, Cloudflare DNS, Azure DNS).
- **Load Balancer / API Gateway**:
  - Layer 7 (NGINX, Traefik, Envoy, AWS ALB, Azure Front Door) capable of SSL termination, WAF, request/response transformation, rate limiting, and circuit breaking.
  - Enable keep‑alive connections to backend to reduce TCP handshake overhead.
  - Use health checks (`/healthz`, `/ready`) to remove unhealthy instances.
- **Service Mesh** (optional for complex microservices):
  - Istio or Linkerd can provide mTLS, traffic splitting, retry policies, observability.
  - Overhead may be unnecessary for current monolith‑ish backend; adopt if service count grows.
- **Geographic Distribution**:
  - Deploy frontend to multiple regions via CDN.
  - Deploy backend instances in multiple regions behind a global load balancer or use anycast IP.
  - Direct traffic to the nearest region using latency‑based routing (Cloudflare Load Balancing, Azure Traffic Manager, AWS Route 53 latency‑based routing).
  - Ensure data replication (Supabase does not currently offer multi‑region write replication; consider active‑passive with periodic snapshots or a separate multi‑region DB solution for future).
- **Bandwidth Costs**:
  - Compress responses (gzip/brotli) – enabled by default in most servers and CDNs.
  - Minimize payload size: paginate large lists, omit unnecessary fields, use binary encodings (protobuf) only if needed.

## Observability-Driven Scaling

- **Metrics to Watch**:
  - `http_request_duration_seconds{endpoint,method,status, le="0.8"}` – proportion of requests under 800 ms SLA.
  - `process_cpu_seconds_total` – overall CPU usage.
  - `process_resident_memory_bytes` – memory usage.
  - `redis_used_memory_ratio` – memory pressure.
  - `celery_queue_length{queue}` – backlog per queue.
  - `pg_replication_lag_seconds` – replica delay (if using replicas).
  - `http_requests_total{status=~"5.."}` – error rate.
  - `business_event_total{event="job_ingested"}`, `event="resume_uploaded"` – throughput.
- **Alerting Thresholds (examples)**:
  - `rate(http_requests_total[5m]) > 1000` and `histogram_quantile(0.95, http_request_duration_seconds_bucket) > 0.8` → scaling trigger.
  - `increase(redis_used_memory_bytes[5m]) / increase(redis_total_memory_bytes[5m]) > 0.8` → consider scaling Redis or evicting unused keys.
  - `sum by (queue) (celery_queue_length) > 100` → add workers.
  - `rate(http_requests_total{status=~"5.."}[5m]) > 0.05 * rate(http_requests_total[5m])` → investigate errors, may need scaling upstream.
- **Automation**:
  - Use **Prometheus Operator** (if on Kubernetes) with `HorizontalPodAutoscaler` referencing custom metrics from Prometheus (`prometheus-adapter`).
  - In non‑K8s environments, use cloud‑native autoscaling policies (AWS Step Functions + CloudWatch, Azure Autoscale, GCP Autoscaler) that read from Prometheus via a monitoring adapter or directly from Stackdriver/Cloud Monitoring.
  - Implement a simple controller that queries Prometheus every 30 s and adjusts desired replica count via the cloud provider’s API (AWS ASC, Azure Scale Set, GCP MIG).

## Cost Optimization

- **Right‑Size Instances**:
  - Start with modest sizes (e.g., `db.m6g.large` for Postgres, `cache.t4g.medium` for Redis) and monitor utilization.
  - Downscale during off‑peak hours using scheduled scaling policies (e.g., reduce worker count at night).
- **Spot Instances / Preemptible VMs**:
  - Use for fault‑tolerant worker batches (embedding recompute, maintenance) where occasional interruption is acceptable.
  - Combine with fallback to on‑demand for critical services (API, DB).
- **Storage Tiering**:
  - Move old raw job JSON (`jobs_raw`) to cheaper storage (AWS S3 Glacier, Azure Archive Blob) after 30 days via lifecycle rule.
  - Archive old job records (`jobs`) to a cold table or separate database after 90 days of inactivity.
- **Database Autoscaling**:
  - Some cloud providers offer auto‑scaling compute for PostgreSQL (e.g., Amazon Aurora Serverless v2, Azure Flexible Server). Consider if cost‑benefit fits.
- **Data Transfer**:
  - Keep data transfer within same region/availability zone to avoid inter‑zone charges.
  - Use private endpoints/VPC peering between services when possible (e.g., backend ↔ Redis ↔ database within same VPC).
- **Monitoring Costs**:
  - Use managed Prometheus (e.g., Amazon Managed Service for Prometheus) or open‑source with retention policies to control storage.
  - Retain high‑resolution metrics for short duration (7 days) and downsampled metrics for longer term (30 days).

## Bottleneck Analysis & Mitigation

| Potential Bottleneck | Symptom | Diagnosis | Mitigation |
|----------------------|---------|-----------|------------|
| **Database Write Throughput** | Rising insert latency, replication lag, high CPU on primary | Check `pg_stat_activity` (wait events), `pg_stat_database` (xact_commit rate) | - Bulk inserts <br> - Partitioning by time <br> - Read replicas for reads <br> - Consider write‑sharding if needed |
| **CPU Saturation on API Instances** | High request latency, CPU > 85%, steady queue length | Review `top`, `pidstat`, check for blocking calls (e.g., synchronous http, heavy regex) | - Add more instances <br> - Offload CPU‑heavy tasks to workers <br> - Optimize algorithms (use compiled regex, avoid O(n^2) loops) |
| **Redis Memory Pressure** | Evictions rising, cache hit ratio dropping, latency ↑ | `INFO memory`, `keyspace_hits/misses` | - Increase Redis size <br> - Review TTLs (increase for less volatile data) <br> - Move less critical caches to RedisCluster with more shards |
| **External API Rate Limits (Apify/OpenAI)** | 429 responses, retry logs, queue backlog | Monitor Apify/OpenAPI response codes, check worker logs | - Implement token bucket per worker <br> - Batch requests where possible <br> - Request higher tier limits or negotiate enterprise contracts <br> - Cache OpenAI embeddings for identical inputs |
| **Network Bandwidth (Egress)** | High outbound traffic, increased cost, occasional timeouts | Cloud provider metrics, `iftop`, `nload` | - Compress responses (gzip/brotli) <br> - Serve static assets via CDN <br> - Optimize image sizes (`next/image`) <br> - Consolidate API responses (avoid over‑fetching) |
| **Job Ingest Backlog** | `job_ingest` queue length grows, delayed fresh jobs | `redis llen job_ingest`, check Apify run durations | - Increase number of ingestion workers <br> - Stagger Apify actor start times (avoid all at once) <br> - Use Apify webhooks if available (push‑based) |
| **Matching Latency** | p95 matching latency > 300 ms, high CPU on matching service | Profile matching endpoint: vector search time, scoring loops | - Increase `ivfflat.lists` and probes <br> - Ensure sufficient `pre_limit` (candidate set) <br> - Cache top‑N matches per user (Redis) <br> - Consider approximate nearest neighbor with higher recall if needed |

## Scaling Triggers & Automation

- **Autoscaling Policies** (examples for Kubernetes with HPA + Custom Metrics):
  - **CPU-Based**: `metrics:
      - type: Resource
        resource:
          name: cpu
          target:
            type: Utilization
            averageUtilization: 70`
  - **Memory-Based** (if needed): similar with `memory`.
  - **Custom Metrics (Prometheus Adapter)**:
    - `type: Pods`
      `podsMetric:
          target:
            type: AverageValue
            averageValue: 50`   (e.g., target average queue length per pod < 50)
    - `type: Object`
      `describedObject:
            apiVersion: batch/v1
            kind: Job
            name: scaling-trigger
          metric:
            name: job_ingest_queue_length
            target:
              type: AverageValue
              averageValue: 100`
- **Scheduled Scaling** (for predictable daily patterns):
  - Reduce worker count at night (00:00–06:00) to save cost, increase before peak (07:00–23:00).
  - Use cloud provider’s scheduled actions (AWS Auto Scaling scheduled actions, Azure Autoscale profiles, GCP cron jobs).
- **Manual Override**:
  - Provide a runbook for operators to manually adjust replica counts via cloud console or `kubectl scale deployment backend --replicas=15`.
- **Testing Scaling Policies**:
  - Use load‑testing tools (k6) to simulate ramp‑up and verify that the autoscaler responds within expected time (e.g., add instances within 2 min of sustained load).

## Future‑Proofing (Beyond 3‑Year Horizon)

- **Multi‑Active‑Active Database** – Investigate technologies like CockroachDB, Yugabyte, or Distributed SQL (Google Spanner) to achieve true multi‑region writes without complex replication lag handling.
- **Serverless Backend** – Migrate portions of the backend to AWS Lambda/Azure Functions (using containers) for truly elastic, pay‑per‑invocation scaling, while keeping long‑running workers on dedicated instances.
- **Edge Computing** – Run matching or recommendation logic at the edge (Cloudflare Workers, Vercel Edge Functions) for ultra‑low latency when data set is small enough to replicate to edge nodes (e.g., top‑100k jobs via CDN).
- **ML Model Serving** – Replace OpenAI calls with self‑hosted LLMs (Llama 3, Mixtral) served via Triton Inference Server or TorchServe to reduce per‑call cost and latency, while retaining ability to update models.
- **Data Mesh / Data Fabric** – As analytics needs grow, consider a decentralized data architecture where each domain (jobs, resumes, matches) owns its own pipelines and shares via contracts.
- **FinOps Automation** – Implement automated rightsizing scripts that recommend instance adjustments based on utilization trends (using CloudWatch/Azure Monitor metrics).
- **Chaos Engineering** – Regularly inject latency, packet loss, or instance termination to verify resilience and autoscaling responsiveness.

## Summary

The scalability plan combines **horizontal stateless scaling**, **database read replicas and partitioning**, **intelligent caching**, **event‑driven worker pools**, and **observability-driven autoscaling** to support the projected growth from tens of thousands to millions of users while keeping latency within SLAs and costs under control. By instrumenting each layer, defining clear scaling triggers, and employing automation, the system can elastically expand and contract with demand, ensuring a responsive experience for job seekers and recruiters alike.

---  
*Document version: 1.0*  
*Last updated: 2026-07-14*