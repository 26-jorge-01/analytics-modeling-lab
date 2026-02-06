# Synthetic & public transactional dataset used as a modeling playground.
**Analytics Modeling Lab**

## Overview

This project is a practical laboratory designed to demonstrate how different data modeling approaches serve different analytical needs.

Rather than presenting a single “best” model, the project shows how the same dataset can be represented through multiple modeling paradigms — each optimized for a specific type of question, decision, and level of analysis.

The objective is to showcase how modeling choices impact:

* The type of questions that can be answered

* The speed and simplicity of analysis

* The ability to track change over time

* The scalability of analytical systems

In short, this project demonstrates how and when to use each modeling approach, not just how to build them.

## Domain Used

The laboratory uses a neutral and familiar transactional domain:

**Online marketplace activity with:**

- Customers

- Products and categories

- Orders and order items

- Payments

- Shipments

- Returns

- Subscriptions and subscription events

This domain is intentionally chosen because it is widely understood and rich enough to represent multiple real-world analytical patterns, while remaining easy to reason about.

The project is not a product and does not simulate a real company.
It is a **controlled analytical environment** to compare modeling strategies.

## Business-Oriented Questions This Lab Explores

Instead of focusing on a single business problem, the lab focuses on classes of questions, such as:

**1. Data Consistency & Integrity**

- Which orders are missing payments?

- Which products are not assigned to a category?

- Are there duplicated customers or transactions?

**2. Change Over Time**

- How has a customer’s profile changed historically?

- How many times has an order changed status?

- How often do subscriptions change plan or state?

**3. Aggregated Performance**

- How many items are sold per day?

- What is the total revenue by product or category?

- How many active subscriptions exist over time?

**4. Hierarchical Analysis**

- Performance by category → subcategory → product

- Rollups and drilldowns across product hierarchies

**5. Multi-Process Analysis**

- How do sales, returns, and shipments relate to each other?

- Where do delays correlate with higher return rates?

Each of these question types is intentionally mapped to a different modeling paradigm.

## Why Multiple Models Exist in This Project

The project implements several data modeling approaches in parallel to demonstrate their **strategic purpose**:

### Third Normal Form (3NF)

Represents clean, normalized domain entities with minimal redundancy.
Optimized for data integrity and consistency.

**Best for:**
Understanding the operational structure of the domain and validating data correctness.

### Data Vault

Separates business keys, relationships, and descriptive attributes while preserving full history.

**Best for:**
Tracking change over time, auditing, and integrating evolving data sources.

### Star Schema

Denormalized dimensional model optimized for analytical consumption.

**Best for:**
Fast aggregation, dashboards, and straightforward analytical queries.

### Snowflake Schema

Normalized dimensional model where complex dimensions are decomposed into hierarchies.

**Best for:**
Hierarchical analysis and governance of shared reference data.

### Galaxy / Fact Constellation

Multiple fact tables sharing conformed dimensions.

**Best for:**
Analyzing multiple business processes together (sales, returns, shipments, subscriptions).

## What This Project Demonstrates

From a business perspective, this project demonstrates the ability to:

- Translate analytical needs into appropriate data models

- Design data structures aligned with specific decision-making patterns

- Balance data integrity, historical tracking, and analytical usability

- Build analytical systems that evolve with changing requirements

From a professional standpoint, it shows:

- Strong understanding of data modeling theory and practice

- Ability to reason about architectural trade-offs

- Experience designing reproducible analytical environments

- Clear thinking about how data supports decision-making

## Who This Project Is For

- Recruiters evaluating data engineering / analytics engineering profiles

- Hiring managers looking for modeling maturity

- Teams interested in how modeling decisions impact analytics

This repository is meant to be explored conceptually first.
Technical implementation details are documented separately.

## One-Sentence Summary

A reproducible analytics laboratory that applies multiple data modeling paradigms to the same dataset in order to demonstrate when and why each modeling approach should be used to answer different types of analytical questions.