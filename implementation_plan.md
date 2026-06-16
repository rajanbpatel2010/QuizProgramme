# IT Skills Assessment Application

This plan outlines the architecture and phased implementation for a role-based, timed, multiple-choice assessment platform designed for IT professionals. The application will evaluate users across various technical domains, adapt difficulty based on their role, and provide AI-generated personalized feedback and learning resources upon completion.

## Architecture & Tech Stack Proposal (Updated for Render)

To ensure seamless hosting on **Render** with a managed database, we are updating the tech stack to a robust, modern full-stack JavaScript/TypeScript ecosystem. 

- **Full-Stack Framework:** Next.js (React) with TypeScript. This allows us to serve both the stunning frontend UI and the backend API logic from a single deployment service on Render.
- **Styling:** TailwindCSS and framer-motion for a premium, dynamic, and engaging UI with micro-animations.
- **Database:** PostgreSQL (managed natively on Render). 
- **ORM:** Prisma ORM for type-safe database access.
- **Authentication:** Auth.js (formerly NextAuth) to handle full Login and Registration.
- **AI Integration & Security:** Integration with Google Gemini.
  - **Key Security:** The Gemini API Key will be strictly secured on the server-side via environment variables. The Next.js API routes will act as a secure proxy, ensuring the API key is never exposed to the client browser.
  - **Feedback Generation:** AI will be used primarily at the end of the test to generate the professional summary and pinpoint strengths/weaknesses based on test performance.

> [!TIP]
> **Aesthetics & UX**
> The UI will feature modern design elements (glassmorphism, curated color palettes, dark mode support) and an interactive timer to create an engaging and premium assessment experience.

## Proposed Implementation Phases

### Phase 1: Foundation & Authentication
- Initialize the Next.js project in `d:/RP_Code/AIApplications/Prep`.
- Provision a local PostgreSQL database (and eventually a Render PostgreSQL instance).
- Setup Prisma ORM and design the schema (`User`, `Role`, `Category`, `Question`, `Answer`, `TestAttempt`, `TestResponse`).
- Implement Auth.js for User Registration and Login.

### Phase 2: Static Seeding & Web Scraping Scripts
- Develop a Node.js data ingestion script (using tools like Cheerio or Puppeteer) to scrape initial questions, answers, and practical examples directly from trusted web sites.
- This script will format the scraped data and insert it into the PostgreSQL database.
- During the test, the application will fetch these pre-populated questions and examples purely from the database (no real-time AI/Web fetching required during test-taking for examples).

### Phase 3: Assessment Core & UI (Test Taking)
- Build the assessment interface featuring:
  - An interactive timer per question.
  - Forward-only progression (disabling back-navigation).
  - Syntax highlighting for practical code examples in questions.
- Create secure API routes in Next.js to fetch questions one-by-one and submit answers.

### Phase 4: Scoring, AI Feedback, & Knowledge Enhancement
- Implement the scoring logic.
- Integrate the AI SDK (e.g., Google Gemini SDK) to process the user's completed test and generate:
  - A professional summary.
  - A breakdown of strengths and areas for improvement.
  - Suggested resources and action items.
- Build the final "Results" UI on the frontend to elegantly display this feedback.
- **Dynamic Knowledge Enhancement (Feasibility: High):** Add an "Enhance Knowledge" button on the results page. When clicked, this will trigger a secure backend worker that uses a Search API (or web scraper) combined with AI to find new, relevant questions/answers on the web based on the test topics, parse them into the structured DB format, and insert them into the database to expand the question bank for future tests.

### Phase 5: Deployment on Render
- Connect the GitHub/GitLab repository to Render.
- Configure environment variables (Database URL, NextAuth Secret, AI API Keys).
- Deploy the Web Service (Next.js) and Database (PostgreSQL) on Render.

## Verification Plan

### Automated Tests
- Unit tests for the scoring calculation logic.

### Manual Verification
- Verify User Login and Registration flows.
- Simulate taking a test as different roles to verify difficulty scaling.
- Verify the timer expires and auto-submits.
- Verify the browser back button does not allow re-answering.
- Review the generated AI feedback for a completed test to ensure it is actionable, accurate, and properly formatted.
