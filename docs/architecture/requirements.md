# Requirements — Bike Network System

## Functional Requirements

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


## Non-Functional Requirements vs Quality of Service Mapping

### QoS Attributes

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


### Non-Functional Requirements

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