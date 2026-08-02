# Module 6: Networking & Distributed Basics

## Module overview
This module prepares semi-senior backend engineers to reason about end-to-end production behavior: request paths, failure domains, data durability, scalable architecture, and cost-aware operations.

## Learning objectives
- Turn requirements into explicit availability, latency, consistency, security, and cost targets.
- Design APIs and asynchronous workflows that survive partial failures and retries.
- Explain production trade-offs in architecture reviews and interviews.

## Required prerequisites
- Python/FastAPI, Docker, HTTP, SQL, Redis, and basic Linux knowledge.
- Modules 2–5 or equivalent experience with APIs, databases, concurrency, and algorithms.

## Recommended learning order
Read chapters in numerical order, implement the exercises, then use [interview_questions.md](interview_questions.md) for active recall and [tasks.md](tasks.md) for end-to-end practice.

## Estimated study time
**110–145 hours**, including diagrams, prototypes, failure injection, load tests, capacity estimates, and interview practice.

## Skills gained
- Network-aware service design and incident diagnosis
- Resilient distributed workflows and safe deployments
- Capacity, cost, security, and recovery planning
- Clear system-design interview communication

## Real-world applications
Payments, messaging, live updates, files, marketplaces, analytics, APIs, and globally deployed services all require these decisions.

## Backend interview focus areas
Clarifying requirements, capacity estimates, data modeling, caching, consistency, queues, failure handling, observability, security, and trade-off communication.

## Chapter index
- [01-Networking Fundamentals](01-Networking Fundamentals.md)
- [02-OSI Model](02-OSI Model.md)
- [03-TCP IP Model](03-TCP IP Model.md)
- [04-IP Addressing](04-IP Addressing.md)
- [05-IPv4 vs IPv6](05-IPv4 vs IPv6.md)
- [06-MAC Addresses](06-MAC Addresses.md)
- [07-Ports and Sockets](07-Ports and Sockets.md)
- [08-TCP](08-TCP.md)
- [09-UDP](09-UDP.md)
- [10-TLS SSL](10-TLS SSL.md)
- [11-HTTP over TCP](11-HTTP over TCP.md)
- [12-HTTPS](12-HTTPS.md)
- [13-DNS](13-DNS.md)
- [14-DHCP](14-DHCP.md)
- [15-NAT](15-NAT.md)
- [16-Latency](16-Latency.md)
- [17-Bandwidth](17-Bandwidth.md)
- [18-Throughput](18-Throughput.md)
- [19-Jitter](19-Jitter.md)
- [20-Packet Loss](20-Packet Loss.md)
- [21-Network Failures](21-Network Failures.md)
- [22-Reverse Proxy](22-Reverse Proxy.md)
- [23-Forward Proxy](23-Forward Proxy.md)
- [24-Load Balancers](24-Load Balancers.md)
- [25-API Gateway](25-API Gateway.md)
- [26-Service Discovery](26-Service Discovery.md)
- [27-Synchronous Communication](27-Synchronous Communication.md)
- [28-Asynchronous Communication](28-Asynchronous Communication.md)
- [29-RPC and gRPC](29-RPC and gRPC.md)
- [30-WebSockets](30-WebSockets.md)
- [31-Server Sent Events](31-Server Sent Events.md)
- [32-Long Polling](32-Long Polling.md)
- [33-Distributed Systems Fundamentals](33-Distributed Systems Fundamentals.md)
- [34-Failure Handling](34-Failure Handling.md)
- [35-Reliability Basics](35-Reliability Basics.md)

## Summary
The objective is not to memorize vendor diagrams. It is to make a system's guarantees, limits, failure behavior, and operational ownership explicit.
