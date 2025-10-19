# My Hyperflask App

## Overview

This is a timeline-based photo submission web application built with Hyperflask, a Python web framework. The application allows users to create and view timeline entries with photos and captions. The project includes user authentication, database models for users and timeline entries, and a modern frontend built with TailwindCSS, DaisyUI, Alpine.js, and HTMX.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Framework
- **Framework**: Hyperflask (Python-based web framework built on Flask)
- **Rationale**: Hyperflask provides an opinionated structure with built-in features for rapid development including database ORM, user authentication, and asset compilation
- **Key Features**: 
  - Automatic database migrations
  - Built-in development server with hot reload
  - Integrated task worker system (Periodiq)
  - CLI commands for common operations (serve, deploy, worker)

### Database Layer
- **ORM**: Hyperflask's built-in ORM (db.Model)
- **Database**: PostgreSQL (configured for Replit hosting)
- **Schema Design**:
  - `User` model extends `UserMixin` for authentication features
  - `TimelineEntry` model extends `UserRelatedMixin` for automatic user relationship handling
  - Timeline entries include: timestamp, status (pending/approved), caption, photo_url, and created_at
- **Rationale**: PostgreSQL chosen for robust relational data handling and Replit compatibility

### Authentication System
- **Solution**: hyperflask-users package
- **Features**: Provides UserMixin with built-in authentication methods
- **User Model**: Minimal implementation (email-based) extending UserMixin

### Frontend Architecture
- **CSS Framework**: TailwindCSS v4 with DaisyUI component library
- **JavaScript**: 
  - Alpine.js for reactive UI components
  - HTMX for server-side interactions and SSE (Server-Sent Events)
  - Bootstrap Icons for iconography
- **Build System**: esbuild for fast JavaScript bundling
- **Rationale**: Modern, lightweight stack that minimizes JavaScript while maintaining interactivity; HTMX enables server-driven UI updates without complex client state management

### Asset Pipeline
- **Build Tool**: Hyperflask's built-in asset compilation system
- **Configuration**: Defined in `app/assets.json`
- **Process**: 
  - CSS: TailwindCSS compilation with custom plugins
  - JavaScript: esbuild bundles Alpine.js and HTMX
  - Development mode includes live reload

### Development Environment
- **Containerization**: Dev Containers for consistent development environment
- **Package Management**: UV (Python package manager)
- **Node Packages**: Managed via npm/package.json
- **IDE Support**: VSCode configurations with Python debugging, Jinja template support
- **Hot Reload**: Both Python and frontend assets auto-reload during development

### Testing Strategy
- **Framework**: pytest with pytest-asyncio
- **Test Structure**: Tests in `/tests` directory
- **Coverage**: Database connectivity, model validation, route availability
- **Fixtures**: Centralized app fixture in conftest.py

### Data Seeding
- **Approach**: Seed script creates test data programmatically
- **Test Data**: 3 users and 20 timeline entries with randomized timestamps
- **Purpose**: Enables immediate testing and development without manual data entry

### Deployment Architecture
- **Target Platform**: Replit (with Docker support)
- **Deployment Command**: `uv run hyperflask deploy`
- **Environment Variables**: DATABASE_URL (dev) and PROD_DATABASE_URL (production) for database separation
- **Worker System**: Background task processing via Hyperflask's worker command

## External Dependencies

### Python Packages
- **hyperflask**: Core web framework
- **hyperflask-users**: User authentication and management
- **pillow**: Image processing library (for photo handling)
- **requests**: HTTP client library
- **pytest / pytest-asyncio**: Testing frameworks

### JavaScript/Node Packages
- **alpinejs**: Lightweight reactive framework for UI interactions
- **htmx.org**: HTML-over-the-wire library for dynamic content
- **htmx-ext-sse**: Server-Sent Events extension for HTMX
- **bootstrap-icons**: Icon library
- **tailwindcss**: Utility-first CSS framework
- **daisyui**: TailwindCSS component library
- **@tailwindcss/typography**: Typography plugin for TailwindCSS
- **esbuild**: JavaScript bundler

### Database
- **PostgreSQL**: Primary data store hosted on Replit
- **Connection**: Managed via DATABASE_URL environment variable
- **Separate environments**: Development and production databases

### Development Tools
- **Dev Containers**: Isolated development environment configuration
- **Docker**: Container runtime (via docker-outside-of-docker feature)
- **UV**: Fast Python package installer and resolver
- **VSCode Extensions**: 
  - Python language support
  - Jinja template syntax highlighting
  - SQL ORM language support

### Template System
- **Hyperflask UI**: Built-in UI components and templates
- **hyperflask_users templates**: Pre-built authentication templates
- **Jinja2**: Template engine (standard with Flask/Hyperflask)