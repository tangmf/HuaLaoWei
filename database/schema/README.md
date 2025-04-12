# 📦 Database Schema for SmartCity Forum and Analytics Platform

This folder contains SQL schema definitions for all structured databases used in the SmartCity Forum and Municipal Analytics Platform. The project will eventually be deployed on Huawei Cloud, with GaussDB for structured data and OBS (Object Storage Service) for unstructured media files.

---

## 📁 Folder Contents

| File Name                | Description |
|-------------------------|-------------|
| `users.sql`             | Schema for user accounts and login metadata |
| `issues.sql`            | Core table for reported issues (private or public) |
| `forum_posts.sql`       | Public-facing posts linked to reported issues |
| `comments.sql`          | Nested commenting system for public posts |
| `post_votes.sql`        | Like/dislike system for posts |
| `comment_votes.sql`     | Like/dislike system for comments |
| `media_assets.sql`      | Metadata for user-submitted images, videos, and audio |
| `analytics_weather.sql` | Weather data (external source) used for trend analysis |
| `analytics_geo.sql`     | Geospatial features such as POI density or facilities |
| `analytics_socio.sql`   | Socioeconomic indicators per region/year |

---

## 🧠 Schema Design Philosophy

- **Modular**: Data is broken into logical tables for maintainability and clarity.
- **Scalable**: Tables are designed to support millions of rows with proper indexing (to be added at deployment).
- **Flexible**: JSONB and GEOGRAPHY types are used to support rich metadata and spatial analysis.
- **Cloud-Ready**: Media files are not stored in the database but linked to Huawei OBS cloud paths.

---

## 🧱 Entity Relationships (Simplified)


## 🔗 Integration Notes

- **Post Visibility**: Only issues marked as `is_public = TRUE` appear in `forum_posts`.
- **Comments**: Comments support recursive replies via `parent_comment_id`.
- **Votes**: Voting is binary (like or dislike) and unique per user per post/comment.
- **Location Fields**: Use Huawei GaussDB PostGIS support (or `lat/lng` fallback).
- **Media Files**: Actual files (e.g., images/videos) are stored on OBS; `media_assets` only stores metadata and file paths.

---

## 🛠 Deployment Plan

Once access to Huawei Cloud is granted:

1. Deploy all tables to **GaussDB**.
2. Configure spatial indexing for `GEOGRAPHY` fields (if supported).
3. Use **OBS buckets** for file uploads; store file URLs in `media_assets`.
4. Use **ModelArts** or custom pipelines for analysis using `analytics_*` tables.

---

## ✍️ Author & Maintainers

- **Lead Architect**: Prism Fifty-five
- **Team**: AI for Smart City (National AI Student Challenge 2025 - Local Track 5, Huawei)

---

## ✅ License

This schema is for academic, research, and innovation purposes. If reused for commercial applications, credit to the original authors is appreciated.