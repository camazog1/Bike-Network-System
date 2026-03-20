# Bike Network System

## Project Description

System for bike rental management and cycling activity promotion. Includes event and route scheduling, an interactive map with Leaflet, and bike inventory control.

## Team

| Role          | Name                |
| ------------- | ------------------- |
| Product Owner | Carlos Alberto Mazo |
| Scrum Master  | Patricia Arango     |
| Developer 1   | Jeison Cifuentes    |
| Developer 3   | Miguel Vasquez      |
| Developer 4   | Jhonnathan Ocampo   |
| QA            | Oswaldo Alzate      |

## Deliverables

### 1. Functional Requirements

| ID    | Requirement                                                                 | Module           |
| ----- | --------------------------------------------------------------------------- | ---------------- |
| RF-01 | The system must allow a user to register with name, email and password      | `authentication` |
| RF-02 | The system must allow a user to authenticate with email and password        | `authentication` |
| RF-03 | The system must allow a user to log out and invalidate the token            | `authentication` |
| RF-04 | The system must allow adding a bike with ID, brand, type, color and status  | `bike-crud`      |
| RF-05 | The system must allow listing all bikes                                     | `bike-crud`      |
| RF-06 | The system must allow editing a bike's information                          | `bike-crud`      |
| RF-07 | The system must allow deleting a bike that is not currently rented          | `bike-crud`      |
| RF-08 | The system must allow an authenticated user to rent an available bike       | `rental`         |
| RF-09 | The system must mark a bike as unavailable when it is rented                | `rental`         |
| RF-10 | The system must allow returning a bike and mark it as available             | `rental`         |
| RF-11 | The system must display the rented bike on an interactive map using Leaflet | `map`            |
| RF-12 | The system must allow consulting scheduled cycling events                   | `events`         |
| RF-13 | The system must allow consulting available cycling routes                   | `events`         |
| RF-14 | The system must allow consulting scheduled competitions                     | `events`         |

### 2. NRF vs QoS Mapping

| QoS Attribute        | Description                                       |
| -------------------- | ------------------------------------------------- |
| **Performance**      | Response time and throughput                      |
| **Availability**     | System uptime and fault tolerance                 |
| **Security**         | Authentication, authorization and data protection |
| **Scalability**      | Ability to handle growing load                    |
| **Maintainability**  | Ease of updating and testing the codebase         |
| **Usability**        | User experience and error handling                |
| **Reliability**      | Consistency and data integrity                    |
| **Interoperability** | Ability to integrate with other systems           |
| **Compatibility**    | Support across browsers and platforms             |

| RNF    | Requirement                                                                     | QoS Attribute    |
| ------ | ------------------------------------------------------------------------------- | ---------------- |
| RNF-01 | The system must respond to any request in less than 2 seconds under normal load | Performance      |
| RNF-02 | The system must be available 95% of the time                                    | Availability     |
| RNF-03 | All passwords must be stored using a hashing algorithm (bcrypt)                 | Security         |
| RNF-04 | All API endpoints except public ones must require JWT authentication            | Security         |
| RNF-05 | The system must support up to 50 concurrent users                               | Scalability      |
| RNF-06 | The interactive map must load in less than 3 seconds                            | Performance      |
| RNF-07 | The system must run on modern browsers (Chrome, Firefox, Edge)                  | Compatibility    |
| RNF-08 | The API must follow REST conventions and return JSON responses                  | Interoperability |
| RNF-09 | The codebase must have at least 70% test coverage                               | Maintainability  |
| RNF-10 | The system must provide meaningful error messages to the user                   | Usability        |
| RNF-11 | The databases must support rollback in case of failed transactions              | Reliability      |
| RNF-12 | The databases must have a migration system                                     | Reliability      |

### 3. Context Diagram

<img width="3288" height="2964" alt="image" src="https://github.com/user-attachments/assets/4c0c877c-65e2-4cd4-8ee4-f1a253c0163d" />

### 4. User Stories

https://github.com/users/camazog1/projects/9

### 5. Component Diagram (Logical and Technical)

### 6. Sequence Diagrams

#### User Authentication

<img width="7840" height="4935" alt="User Authentication-2026-03-20-023028" src="https://github.com/user-attachments/assets/203f80b4-90e8-4902-b368-8cfa80d16e95" />

#### Bike Rental by Authenticated User 

<img width="8192" height="3051" alt="Bike Rental by Authenticated User-2026-03-20-022007" src="https://github.com/user-attachments/assets/4d5088ca-d572-47ce-b1c0-286da68b201f" />

#### Events & Map Consultation

<img width="8192" height="5614" alt="Events   Map Consultation-2026-03-20-022235" src="https://github.com/user-attachments/assets/e2373773-e7b9-4155-827c-9cdc838a2ce0" />

### 7. Deployment Diagram

![Deployment Diagram](https://github.com/user-attachments/assets/c0d8136e-3f89-4aa8-8446-667d2ed14acd)


## Architecture Decisions

### Stack Selection

| Layer          | Technology         | Rational                                                                                 |
| -------------- | ------------------ | ---------------------------------------------------------------------------------------- |
| Services       | Python + Flask     | Lightweight, strong community and REST API support                                       |
| Frontend       | TypeScript + React | Type safety, component reusability, large ecosystem, and industry standard                |
| Databases      | MySQL              | Relational model fits our domain, ACID compliance, transaction rollback support (RNF-11) |
| Maps           | Leaflet            | Open source, lightweight, no API key required, easy React integration                    |
| Auth           | JWT                | Stateless authentication, easy to implement with Flask                                   |
| Message Broker | RabbitMQ           | Async communication for rental/return notifications and real-time map events             |
| Orchestration  | Kubernetes (EKS)   | Container orchestration, scalability, high availability, and self-healing                 |

### Technological Strategy

- **Usage of the microservices model and a decoupled static frontend** — Flask services expose a REST API consumed by the static frontend. Ensuring scalability, availability and security.
- **TypeScript over JavaScript** — enforces type safety, reduces runtime errors, and improves maintainability (RNF-09)
- **MySQL over NoSQL** — The data models are relational (users, bikes, rentals, events, routes) and require transactional integrity
- **Leaflet over Google Maps** — Reliable and open source with no usage cost
- **RabbitMQ for async events** — Decouples rental/return flow from notifications and map updates, improving system responsiveness
- **Kubernetes over bare containers** — enables horizontal scaling, rolling deployments, and automatic recovery

### Deployment Strategy

| Component                 | Deployment                | Rational                                                                              |
| ------------------------- | ------------------------- | ------------------------------------------------------------------------------------- |
| Static Frontend (React)   | AWS S3                    | Ensures a cost-efficient deployment focused on security, scalability and availability |
| Backend (Flask)           | AWS EKS                   | Horizontal scaling, supports 50 concurrent users                                      |
| Database (MySQL)          | AWS RDS                   | Managed service, automatic backups, high availability                                 |
| Message Broker (RabbitMQ) | RabbitMQ Cluster Operator | Deployed as a pod within the cluster, close to producers and consumers                |

- **Cloud over On-Premise** — no physical infrastructure available, AWS reduces operational complexity
- **S3 over container-hosted frontend** — the React build is a static bundle; S3 serves it cheaply without a running container
- **EKS over self-managed Kubernetes** — AWS manages the control plane, reducing DevOps overhead
- **RDS over self-hosted MySQL** — automated backups, multi-AZ support, and managed patches
- **RabbitMQ Cluster Operator over Amazon MQ** — native Kubernetes operator keeps the broker inside the cluster, close to producers and consumers, with no extra managed-service cost
- **All components in the same AWS region** — minimizes latency between services
