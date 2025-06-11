# Kubernetes Monitoring and Remediation Project (KODA)

## Project Overview

This document provides a comprehensive overview of the Kubernetes monitoring and remediation project (KODA - Kubernetes Operations & Detection Agent), outlining its purpose, current status, key components, and the technologies involved. It is designed to help any new contributor or AI understand the project context quickly and effectively.

## 1. Project Aim and Purpose

The primary goal of this project is to develop a robust system for monitoring Kubernetes clusters, detecting anomalies, and automating remediation actions. This aims to:

- **Enhance Cluster Stability:** Proactively identify and address issues before they impact services.
- **Improve Operational Efficiency:** Automate routine tasks and reduce manual intervention.
- **Provide Actionable Insights:** Offer clear visibility into cluster health and performance.
- **Enable Intelligent Remediation:** Implement AI/ML-driven solutions for automated problem resolution.

## 2. Current State and Issues

Currently, the project is focused on enhancing the frontend dashboard and integrating AI capabilities. Recent activities include:

- **Frontend UI/UX Enhancements:** Modernizing the dashboard's look and feel using Tailwind CSS for improved interactivity and visual appeal. This includes updates to the navigation bar, footer, main dashboard page, and metric card components.
- **New Page Implementations:** Addition of dedicated pages for anomalies, remediations, clusters, and settings to provide structured views of relevant data.
- **Chatbot Integration:** Implementing a chatbot powered by a Llama 3.3 Nemotron API key to answer questions about the cluster, anomalies, and remediation, making the system more interactive.
- **Sidebar Integration:** Adapting the UI to include a new sidebar component for improved navigation and user experience, mimicking a modern dashboard layout.
- **Authentication Middleware:** Implemented Next.js middleware to ensure the login page is the initial view for unauthenticated users, with proper route protection for authenticated content.

### Current Issues

1. **503 API Error in Chatbot:**

   - The chatbot is returning a 503 Service Unavailable error when attempting to send messages.
   - Error occurs in the `sendChatMessage` function in the frontend.
   - Root cause: The LlamaLLM initialization is failing in the backend with an error: "cannot import name 'model_validator' from 'pydantic'"
   - This is likely a version compatibility issue with the pydantic library.

2. **Kubernetes Logo Update:**
   - Need to update the Kubernetes logo on the login page to use the provided Kubernetes wheel symbol.
   - Current implementation uses CSS to create a stylized logo, but we need to use the actual Kubernetes wheel symbol.

## 3. Project Architecture

### Frontend

The frontend is built using Next.js and React with Tailwind CSS for styling. Key components include:

1. **Dashboard Pages:**

   - Main dashboard with overview metrics
   - Anomalies page for viewing detected issues
   - Remediations page for viewing and approving remediation actions
   - Clusters page for managing Kubernetes clusters
   - Settings page for configuring the application
   - Login page for user authentication

2. **Authentication System:**

   - Next.js middleware (`src/middleware.ts`) for route protection and authentication checks
   - Authentication context (`src/contexts/AuthContext.tsx`) for managing auth state
   - Cookie-based authentication for server-side validation
   - Client-side redirects for authenticated/unauthenticated users

3. **Chatbot Component:**

   - Interactive chatbot for querying cluster information
   - Implemented in `src/components/chatbot/Chatbot.tsx`
   - Uses the LLaMA API for natural language processing

4. **API Services:**
   - `src/api/services/llama.ts` - Service for interacting with the LLaMA API
   - `src/api/services/metrics.ts` - Service for fetching metrics data
   - `src/api/services/remediations.ts` - Service for managing remediation actions

### Backend

The backend is built using Flask and Python with Kubernetes API integration. Key components include:

1. **API Server:**

   - `src/api_server.py` - Main API server with routes for metrics, remediations, and clusters
   - `k8s-dashboard-backend/api/llama_routes.py` - Routes for the LLaMA API integration

2. **Agents:**

   - `src/agents/anomaly_detection_agent.py` - Agent for detecting anomalies in Kubernetes clusters
   - `src/agents/remediation_agent.py` - Agent for generating remediation actions
   - `src/agents/k8s_multi_agent_system.py` - Multi-agent system for coordinating anomaly detection and remediation

3. **LLaMA Integration:**
   - `src/agents/k8s_multi_agent_system.py` - Contains the LlamaLLM class for interacting with the LLaMA API
   - Uses either OpenAI or LangChain libraries for API integration
   - Supports NVIDIA API keys for the Nemotron model

## 4. Technologies Used

### Frontend

- **React.js:** For building user interfaces
- **Next.js:** For server-side rendering and static site generation
- **Tailwind CSS:** For styling and UI components
- **Three.js / React-Three-Fiber:** For 3D visualizations
- **D3.js:** For data visualization

### Backend

- **Flask:** For the API server
- **Kubernetes Python Client:** For interacting with Kubernetes clusters
- **LLaMA API:** For natural language processing and chatbot functionality
- **Prometheus:** For metrics collection

### AI/ML

- **LLaMA 3.3 Nemotron:** For natural language processing and chatbot functionality
- **Custom anomaly detection models:** For identifying issues in Kubernetes clusters

## 5. Development Guidelines

This project adheres to strict DevOps rules and best practices to ensure consistency, maintainability, and efficiency. Key areas to follow include:

- **Version Control (Git):** Adherence to a clear branching strategy (e.g., GitFlow), clear and concise commit messages, mandatory code reviews, and frequent, small commits.
- **Continuous Integration/Continuous Deployment (CI/CD):** Automated builds, comprehensive automated testing (unit, integration, E2E), Docker for containerization, automated deployments (Kubernetes manifests, blue/green or canary releases), and Pipeline as Code.
- **Infrastructure as Code (IaC):** Managing all Kubernetes resources via YAML manifests, using tools like Helm or Kustomize for configuration, and striving for environment parity.
- **Monitoring and Alerting:** Integration with Prometheus for metrics, Grafana for visualization, Alertmanager for critical alerts, and centralized logging.
- **Security:** Regular Docker image scanning, secure secrets management (Kubernetes Secrets/HashiCorp Vault), strict RBAC policies, network policies, and least privilege principles.
- **Testing:** Comprehensive testing strategy including unit, integration, end-to-end, performance, and optionally chaos engineering.
- **Documentation:** Maintaining up-to-date READMEs, API documentation, runbooks, and architecture diagrams.
- **Environment Management:** Separate environments for development, staging, and production with environment-specific configurations and resource quotas.

## 6. Next Steps

1. **Fix the 503 API Error:**

   - Update the pydantic library to a compatible version
   - Improve error handling in the frontend to provide better user feedback
   - Add graceful degradation when the LLaMA API is unavailable

2. **Update the Kubernetes Logo:**

   - Create an SVG file based on the provided Kubernetes symbol
   - Update the KubernetesLogo.tsx component to use this SVG
   - Ensure the spinning animation works with the new logo

3. **Enhance Authentication System:**

   - ✅ Implemented Next.js middleware for route protection
   - ✅ Updated AuthContext to use both localStorage and cookies
   - ✅ Added client-side redirects on the login page
   - Add user roles and permissions for different dashboard features
   - Implement proper token validation with JWT
   - Add password reset functionality
   - Create user management interface

4. **Enhance Anomaly Detection:**

   - Improve the accuracy of anomaly detection models
   - Add support for more types of anomalies
   - Implement real-time anomaly detection

5. **Expand Remediation Capabilities:**

   - Add more remediation actions
   - Improve the accuracy of remediation suggestions
   - Implement automated remediation for common issues

6. **Improve Documentation:**
   - Add more detailed documentation for each component
   - Create runbooks for common operational tasks
   - Add architecture diagrams

This workspace.md file serves as a living document and will be updated as the project evolves.
