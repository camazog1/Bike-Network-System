# Bike Network System

## Project Description

System for bike rental management and cycling activity promotion. Includes event and route scheduling, interactive map with Leaflet, and bike inventory control.

## Team

| Role | Name |
|------|------|
| Product Owner | Carlos Alberto Mazo |
| Scrum Master | Patricia Arango |
| Developer 1 | Jeison Cifuentes |
| Developer 3 | Miguel Vasquez |
| Developer 4 | Jhonnathan Ocampo |
| QA | Oswaldo Alzate |

## Repository Structure

```
bike-network-system/
├── docs/
│   ├── architecture/
│      ├── requirements.md
│      ├── context-diagram.png
│      ├── use-case-diagram.png
│      ├── component-diagram.png
│      ├── sequence-diagrams.png
│      └── deployment-diagram.png
├── backend/
├── frontend/
├── .github/
├── .gitignore
└── README.md
```

## Deliverables

### 1. Functional Requirements

| ID | Requirement | Module |
|----|-------------|--------|
| RF-01 | The system must allow a user to register with name, email and password | `authentication` |
| RF-02 | The system must allow a user to authenticate with email and password | `authentication` |
| RF-03 | The system must allow a user to log out and invalidate the token | `authentication` |
| RF-04 | The system must allow adding a bike with ID, brand, type, color and status | `bike-crud` |
| RF-05 | The system must allow listing all bikes | `bike-crud` |
| RF-06 | The system must allow editing a bike's information | `bike-crud` |
| RF-07 | The system must allow deleting a bike that is not currently rented | `bike-crud` |
| RF-08 | The system must allow an authenticated user to rent an available bike | `rental` |
| RF-09 | The system must mark a bike as unavailable when it is rented | `rental` |
| RF-10 | The system must allow returning a bike and mark it as available | `rental` |
| RF-11 | The system must display the rented bike on an interactive map using Leaflet | `map` |
| RF-12 | The system must allow consulting scheduled cycling events | `events` |
| RF-13 | The system must allow consulting available cycling routes | `events` |
| RF-14 | The system must allow consulting scheduled competitions | `events` |

### 2. NRF vs QoS Mapping

| QoS Attribute | Description |
|---------------|-------------|
| **Performance** | Response time and throughput |
| **Availability** | System uptime and fault tolerance |
| **Security** | Authentication, authorization and data protection |
| **Scalability** | Ability to handle growing load |
| **Maintainability** | Ease of updating and testing the codebase |
| **Usability** | User experience and error handling |
| **Reliability** | Consistency and data integrity |
| **Interoperability** | Ability to integrate with other systems |
| **Compatibility** | Support across browsers and platforms |

| RNF | Requirement | QoS Attribute |
|-----|-------------|---------------|
| RNF-01 | The system must respond to any request in less than 2 seconds under normal load | Performance |
| RNF-02 | The system must be available 95% of the time | Availability |
| RNF-03 | All passwords must be stored using a hashing algorithm (bcrypt) | Security |
| RNF-04 | All API endpoints except public ones must require JWT authentication | Security |
| RNF-05 | The system must support up to 50 concurrent users | Scalability |
| RNF-06 | The interactive map must load in less than 3 seconds | Performance |
| RNF-07 | The system must run on modern browsers (Chrome, Firefox, Edge) | Compatibility |
| RNF-08 | The API must follow REST conventions and return JSON responses | Interoperability |
| RNF-09 | The codebase must have at least 70% test coverage | Maintainability |
| RNF-10 | The system must provide meaningful error messages to the user | Usability |
| RNF-11 | The database must support rollback in case of failed transactions | Reliability |

### 3. Context Diagram

<img width="3288" height="2964" alt="image" src="https://github.com/user-attachments/assets/4c0c877c-65e2-4cd4-8ee4-f1a253c0163d" />

### 4. Use Case Diagram / User Stories
### 5. Component Diagram (Logical and Technical)
### 6. Sequence Diagrams
### 7. Deployment Diagram
<img width="1982" height="1864" alt="Diagrama de despliegue finall" src="https://github.com/user-attachments/assets/30ed249c-8126-4b0f-8119-9a4a9dd68ab5" />

## Architecture Decisions

### Stack Selection

| Layer | Technology | Rational |
|-------|-----------|----------|
| Backend | Python + Flask | Lightweight, easy to learn, fast prototyping, strong community and REST API support |
| Frontend | TypeScript + React | Type safety, component reusability, large ecosystem and industry standard |
| Database | MySQL | Relational model fits our domain, ACID compliance, transaction rollback support (RNF-11) |
| Maps | Leaflet | Open source, lightweight, no API key required, easy React integration |
| Auth | JWT | Stateless authentication, easy to implement with Flask |
| Message Broker | RabbitMQ | Async communication for rental/return notifications and real-time map events |
| Orchestration | Kubernetes (EKS) | Container orchestration, scalability, high availability and self-healing |

### Technological Strategy

- **Backend and frontend are decoupled** — Flask exposes a REST API consumed by React, allowing independent development and deployment
- **TypeScript over JavaScript** — enforces type safety, reduces runtime errors and improves maintainability (RNF-09)
- **MySQL over NoSQL** — our data model is relational (users, bikes, rentals) and requires transactional integrity
- **Leaflet over Google Maps** — open source with no usage cost, sufficient for academic scope
- **RabbitMQ for async events** — decouples rental/return flow from notifications and map updates, improving system responsiveness (RNF-01)
- **Kubernetes over bare containers** — enables horizontal scaling, rolling deployments and automatic recovery

### Deployment Strategy

| Component | Deployment | Rational |
|-----------|-----------|----------|
| Frontend (React) | AWS EKS | Containerized, scalable, managed by Kubernetes |
| Backend (Flask) | AWS EKS | Horizontal scaling, supports 50 concurrent users (RNF-05) |
| Database (MySQL) | AWS RDS | Managed service, automatic backups, high availability (RNF-02) |
| Message Broker (RabbitMQ) | AWS EKS | Deployed as a pod within the cluster, close to producers and consumers |

- **Cloud over On-Premise** — no physical infrastructure available, AWS reduces operational complexity
- **EKS over self-managed Kubernetes** — AWS manages the control plane, reducing DevOps overhead
- **RDS over self-hosted MySQL** — automated backups, multi-AZ support and managed patches
- **All components in the same AWS region** — minimizes latency between services (RNF-01)
