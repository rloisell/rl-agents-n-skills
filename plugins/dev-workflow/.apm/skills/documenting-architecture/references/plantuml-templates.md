# PlantUML & Mermaid Skeleton Templates

Reference templates for standard PlantUML and Mermaid diagram types. Copy the
appropriate skeleton, rename, and fill in project specifics.

## Contents

- [Sequence diagram](#sequence-diagram) • [Class diagram](#class-diagram) • [State diagram](#state-diagram) • [C4 Context](#c4-context) • [Mermaid architecture quickview](#mermaid-architecture-quickview)

## Sequence diagram

```plantuml
@startuml
title Feature Name — Key Operation Sequence

actor User
participant Frontend
participant "API :Controller" as API
participant "Service" as Svc
database "MariaDB" as DB

User -> Frontend : action
activate Frontend

Frontend -> API : POST /api/resource (dto)
activate API

API -> Svc : DoSomethingAsync(dto)
activate Svc

Svc -> DB : INSERT / SELECT
DB --> Svc : result
Svc --> API : dto
deactivate Svc

API --> Frontend : 200 OK { ... }
deactivate API

Frontend --> User : updated UI
deactivate Frontend

@enduml
```

## Class diagram

```plantuml
@startuml
title Domain Class Model — <Project>

package "Domain" {
    class Entity {
        +Id : Guid
        +Name : string
        +CreatedAt : DateTime
        +UpdatedAt : DateTime?
        +IsActive : bool
        +Deactivate() : void
    }

    class RelatedEntity {
        +Id : Guid
        +EntityId : Guid
        +Value : string
    }

    Entity "1" --> "0..*" RelatedEntity : contains
}

package "API" {
    class EntityController {
        -_service : IEntityService
        +GetAll() : Task<IActionResult>
        +GetById(id : Guid) : Task<IActionResult>
        +Create(dto : CreateRequest) : Task<IActionResult>
        +Update(id : Guid, dto : UpdateRequest) : Task<IActionResult>
        +Delete(id : Guid) : Task<IActionResult>
    }

    interface IEntityService {
        +GetAllAsync() : Task<EntityDto[]>
        +GetByIdAsync(id : Guid) : Task<EntityDto>
        +CreateAsync(r : CreateRequest) : Task<EntityDto>
        +UpdateAsync(id : Guid, r : UpdateRequest) : Task<EntityDto>
        +DeleteAsync(id : Guid) : Task
    }

    EntityController --> IEntityService
}

package "Infrastructure" {
    class EntityService {
        -_db : ApplicationDbContext
    }

    EntityService ..|> IEntityService
}

@enduml
```

## State diagram

```plantuml
@startuml
title Entity Lifecycle — <EntityName>

[*] --> Draft : created

Draft --> PendingReview : submit()
Draft --> Cancelled : cancel()

PendingReview --> Active : approve()
PendingReview --> Draft : requestChanges()
PendingReview --> Cancelled : cancel()

Active --> Suspended : suspend()
Active --> Completed : complete()

Suspended --> Active : reinstate()
Suspended --> Cancelled : cancel()

Completed --> [*]
Cancelled --> [*]

note right of PendingReview
  Notifications sent to
  assignee on entry
end note

@enduml
```

## C4 Context

```plantuml
@startuml
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Context.puml
LAYOUT_WITH_LEGEND()
title System Context — <Project>

Person(user, "End User", "Uses the system via browser")
Person(admin, "Administrator", "Manages configuration")

System_Boundary(sys, "<Project>") {
    System(frontend, "React SPA", "Single page application")
    System(api, "REST API", "Backend service")
    System(db, "Database", "Relational data store")
}

System_Ext(idp, "OIDC Identity Provider", "Authentication (OIDC / PKCE)")
System_Ext(platform, "Container Platform", "Managed Kubernetes / OpenShift")

Rel(user, frontend, "Uses", "HTTPS 443")
Rel(admin, frontend, "Manages", "HTTPS 443")
Rel(frontend, api, "API calls", "HTTPS 443")
Rel(api, db, "Reads/writes", "TCP 3306")
Rel(frontend, idp, "Auth", "OIDC / PKCE")
Rel(api, idp, "Token validation", "JWKS")

@enduml
```

## Mermaid architecture quickview

```mermaid
graph TB
    subgraph "Client"
        U[User Browser]
    end
    subgraph "Container Platform"
        subgraph "Tools Namespace"
            GH[CI Runner]
        end
        subgraph "DEV / TEST / PROD Namespace"
            FE[Frontend :8080]
            API[API :8080]
            DB[(Database :3306)]
        end
    end
    subgraph "External"
        IDP[OIDC Provider]
        REG[Container Registry]
    end

    U -->|HTTPS| FE
    FE -->|REST| API
    API -->|SQL| DB
    FE -->|OIDC| IDP
    GH -->|push image| REG
    API -->|pull image| REG
```
