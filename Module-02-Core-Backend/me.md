## MVC
### MVC is a design pattern, where we use Controller, repo, and service.
### service: contain all busnice logic
### repo: the only components that deals with DB
### Controller: recieve the HTTP requests and give responce

# --------

## Background Workers and Cron Jobs

### Background Workers is a worker that pick up a job after api responce
### Cron job, is a job that is sheduled to be run on a specific time

## ------------------


## Monitoring, Error Handling, Logging

## Logging >> record of the action (user actions, database quiries, api calls, system events)

### Structured Loggins

#### Traditional Approach >> consol.log

#### Structured Approach >> {level: 'info', msg: "user logged in", "userId":12, timestamp: "2021-01-15"}

#### we have logging tools ex: ELK stack, Datadog, CloudWatch

#### Correlation IDs
##### let you trace the entire journey by searching for one unique identifier accross all logs


## Error Handling Basics
## 1. Try/catch Block
## 2. Never expose Internals (stack traces and database errors should never reach the client-security risks)
## 3. Return Clear Json (transform errors into consistent user friendly response)
## 4. Global Error Middleware (single handler that catches all unhandldled errors across the app)

### NOTES:
### 400: Bad input from user
### 404: Resource not found
### 500: server-side issues


## we have two types of errors:
## 1. Operational Errors
## 2. Operationals erros


### Monitorting
# Latency
# Throughput
# Error Rate
# Resources


### Simple Monitoring Patterns in Node.js

# 1.Log Request Duration
# 2.Flag slow endpoints
# 3.Track Recurring Errors
# 4.Health Check Route


## ----------------------

### SOLID principles and code quality
### S: single respossibility (controller, service, repo, provider)
### o: Open/Closed Principle (OCP) ex:(New Login  Method, New paymeny method, Implementing Vaching, New Notification Channel)
### L: Liskov Substitution (we can swap modules witout breaking the system) ex: (replace Mysql repo with postgres repo, swap email provider, swap cloud provider)
### I: Interface Segregation (module depend only on what they use) ex: ()!
### D: Dependency Inversion Princible (High Level logic should not depend on low-level details) ex( )

## ----------------------
## ----------------------
## ----------------------


# DataBases

## Schema Design Basics (SQL)
what is schema
what is PK (primary key)
what is FK (Foregin key)
Constraints:
- NotNull
- Unique (email addresses, username)
- Check (price > 0)
- Default (created_at) >> some fields I dont have to give a value.

Normalization:
- First Normal Form: (All Column Values Are Atomic -user addresses (should not be list)-)
- Second Normal Form: (No column should depends on part of coposite primary key)
ex: OrderItems >> pk (order_id, product_id)
order_id    product_id  quantity    product_name
101         55          2           iPhone 14


- Third Normal Form: (NO column should depend on another non-key column)
ex: Employees

empoyee_id  depertent_id  department_name
50          3               Marketing



## WHen to Denormalize
- Read-Heacvy Analytics
- Avoid Expensive Joins
- Caching Precomputed Values
- NoSQL-like flexibility



## -----------------------
## ----------------------
# SQL Essentials (DDL + DML)

## One-to-one Relationships
ex: User, UserProfile

## One-to-many (1:N) Relationships
ex: User, Orders

## Many-to-many (N:N) Relationships
ex: Categories, Product

Aseperate Join Table (product_category)


## Inheritance (table per type stategy)
ex: Usertable > Student Table, Teacher Table

### DDL >> create tables
### DDM >> insert data