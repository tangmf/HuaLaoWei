# Hualaowei Smart City Municipal Project
**Track 2: Improve Citizen Engagement and Civic Services**

This repository contains the full stack codebase for the Hualaowei Smart City solution, designed to improve municipal reporting, citizen engagement, and proactive city management through a cloud-native and AI-powered architecture.  

---

## Table of Contents
- [Overview](#overview)
- [Project Structure](#project-structure)
- [Main Components](#main-components)
- [System Workflow](#system-workflow)
- [Deployment Guide](#deployment-guide)
- [Contributors](#contributors)
- [Acknowledgements](#acknowledgements)
---

## Overview

Hualaowei enhances citizen engagement with features such as real-time issue reporting, AI-driven analysis, and predictive urban planning. Built fully on Huawei Cloud services, it ensures scalability, flexibility, and long-term maintainability.

---

## Project Structure
```
/ (root)
├── ai_models/               # AI model training and inference pipelines (chatbot, CV, forecasting)
├── database/                # Database models, migrations, and schemas
├── docs/                    # Documentation, diagrams, and references
├── hualaowei_app/           # React Native app source code (Expo, Tailwind CSS)
├── hualaowei_dashboard/     # Web-based dashboard for municipal staff (React, Tailwind CSS)
├── global_utils/            # Shared utility functions across backend services
├── infra/                   # Infrastructure as Code (deployment scripts, serverless configs)
└── README.md                # Project documentation (this file)
```

---

## Main Components

### Hualaowei App (Mobile)
- Citizen-facing application.
- Report municipal issues with geotagged photos.
- Engage with the public forum.

### Hualaowei Dashboard (Admin Web Portal)
- Visualisation of active and historical reports.
- Access to predictive analytics for planning and resource allocation.

### AI Models
- **Chatbot Assistant**: Multilingual Large Language Model (LLM) integrated with Retrieval-Augmented Generation (RAG).
- **Computer Vision Model**: Automatic categorisation and severity assessment from images.
- **Forecasting Model**: 7-day predictive analysis on issue trends based on weather, geospatial, and socioeconomic data.

### Backend and Utilities
- FastAPI-based and Express.js microservices.
- PostgreSQL (hosted on Huawei RDS) for structured data.
- OBS for media storage.
- FunctionGraph for serverless processing.
- CSS (Cloud Search Service) as the vector database.

---

## System Workflow
NOTE: This is just a temporary draft of the workflow, the dashboard and the app will be 2 separate components.
```
Citizen (Mobile App)
    ↓
API Gateway (Huawei Cloud)
    ↓
Backend Services (FunctionGraph, ECS)
    ↓
Storage & Processing
    - PostgreSQL (Database)
    - OBS (Image/Media Storage)
    - CSS (Embeddings Search)
    ↓
AI Model Inference (Chatbot, CV, Forecasting)
    ↓
Visualisation (Dashboard)
```
---

## Deployment Guide

Currently it's only available on Huawei Cloud, but a local deployment will be made available. 

---

## Contributors
- **Fleming Siow**
- **Jerick Cheong**
- **Tang Ming Feng**
- **Woo Yan Seun**

---

## Acknowledgements
- [Open311 Standard](https://www.open311.org/)
- [OpenStreetMap](https://www.openstreetmap.org/)
- [Huawei Cloud](https://www.huaweicloud.com/intl/en-us/)

---

