
It enables:

- **Founders** to ask business questions without writing SQL  
- **Analysts** to inspect exact queries and resolved tables  
- **Developers** to integrate semantic querying via APIs  

All answers are generated directly from the **source-of-truth database**, not from approximated embeddings or cached documents.

---

## ✅ Core Features (V1)

- Universal **Semantic Plan Engine**
- Automatic **Schema Introspection**
- Semantic → SQL Translation
- Deterministic Query Generation
- Secure, Read-Only SQL Execution
- Structured Machine Output with Human-Readable Summary

> No Vector Search.  
> No Document Chat.  
> No Guesswork.

---

## 🏗️ High-Level Architecture

1. Natural Language Input  
2. Semantic Plan Generation (JSON-based)  
3. Schema Mapping & Resolution  
4. Deterministic SQL Builder  
5. SQL Safety Validation  
6. Secure Database Execution  
7. Structured Result Output  

---

## 🎯 Design Principles

- **Deterministic over probabilistic**
- **Explainable over opaque**
- **Source-of-truth over approximated recall**
- **Security-first execution**
- **Database-native semantics**

---

## 🧪 Project Status

WhareIQ **V1 is functionally complete**.

All core components — from semantic planning to secure SQL execution — have been implemented and validated.

Development is tracked exclusively via **GitHub Issues**, with each system step implemented incrementally and reviewed.

---

## 🔐 Security Model (V1)

- Read-only database connections
- Strict `SELECT`-only query enforcement
- Table & column allow-listing
- Hard row limits
- Query execution timeouts
- SQL validation before execution

---

## 📌 Long-Term Vision

WhareIQ aims to become a **universal semantic intelligence layer for data warehouses**, powering:

- AI-powered Business Intelligence
- Operational & exploratory analytics
- Embedded analytics for SaaS platforms
- Deterministic decision intelligence systems

---

## 📂 Repository Discipline

- No hidden logic
- No silent query execution
- No black-box reasoning
- Every query is inspectable, explainable, and auditable

---

