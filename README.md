# Vestigas Backend Coding Challenge

## Architecture Overview

- **FastAPI entrypoint** (`backend/main.py`) exposes administrative actions plus `/deliveries` and `/deliveries/jobs` listing endpoints with pagination guards.
- **Adapters** coordinate infrastructure concerns:
  - `backend/adapters/repostory/jobs` persists job lifecycle data.
  - `backend/adapters/repostory/unified_deliveries` introduces PostgreSQL repositories for unified deliveries populated during each job run.
  - `backend/adapters/scheduling/job_scheduler.py` orchestrates scheduled fetches, captures per-partner statistics, and persists results.
- **Application layer** contains use cases such as `FetchPartnerDeliveriesUseCase` and `StoreUnifiedDeliveriesUseCase`, together forming the fetch→transform→store workflow through mapper/processor utilities.
- **Domain models** (`backend/domain`) represent partner deliveries, unified deliveries, and statistics, keeping behaviour centralised and reusable across adapters.
- **Ports** (`backend/ports`) define boundaries for adapters and use cases, keeping the core decoupled from infrastructure.

This structure aligns with a clean architecture approach: HTTP, scheduling, and persistence live in adapters; business logic is expressed in the application and domain layers; dependency injection from FastAPI wires everything together.

## Deferred Functional Requirements

Due to time constraints and the breadth of the assessment, a few items were left as future improvements:

- Broader automated test coverage for the new unified delivery flow (especially end-to-end verification).
- Data validation and error reporting for the public listing endpoints.
- Hardening around concurrent job execution, including idempotency guarantees and deduplication.

Although incomplete, the implemented features should convey my engineering approach, design preferences, and code quality standards under limited time.

## Personal Note

This was my first experience building with FastAPI. The framework proved approachable, and I focused on structuring the project to mirror patterns I use in other Python services. I hope the submitted solution offers a clear view of my coding style and architectural thinking even with the outstanding tasks above.
