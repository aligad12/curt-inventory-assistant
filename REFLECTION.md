# 📝 Project Reflection & Design Decisions

### 1. Architecture Overview & Decoupling
This project was intentionally built following a strict **Three-Tier Software Architecture** (Data Layer, Logic Layer, and Presentation Layer). 
* `database.py` isolates all raw SQLite connections, SQL commands, and transaction lifetimes.
* `tools.py` acts as an **Abstraction Layer**, transforming raw rows into structured business-friendly payload capsules.
* `backend.py` serves strictly as a network controller via **FastAPI** to orchestrate incoming requests.

By maintaining these clean boundaries, the AI engine is completely decoupled from the data engine. If this system were migrated to a heavy production database engine like PostgreSQL in the future, the AI configuration rules and FastAPI routes would remain completely untouched.

### 2. Deterministic (Regex) vs. Probabilistic (LLM) Systems
Building both tracking phases exposed a clear contrast between traditional rule-based programming and modern generative AI orchestration:
* **Phase 1 (Rule-Based):** The RegEx model is highly **deterministic**. It is lightning fast, consumes near-zero computing resources, and responds with 100% predictability. However, it is incredibly brittle. A user saying *"Can you tell me the location of the ECU?"* completely breaks the strict `where (?:is|are)` regex anchor, triggering a fallback failure.
* **Phase 2 (Gemini LLM):** The generative model is **probabilistic** and remarkably resilient. It seamlessly interprets semantic intent, handles varying conversational structures, extracts raw parameters dynamically, and maintains long-term stateful context across multiple chat turns (such as tracking pronouns like *"where are they?"* back to *"Brake Pads"*).

### 3. Defensive Programming & Security Boundaries
A primary engineering focus was establishing hard security guardrails between Gemini and the underlying data layer:
* **Anti-SQL Injection Boundary:** The LLM is treated as an untrusted operator. It is given zero direct access to execute SQL queries or view database schemas. Instead, it is given an abstract interface via `tools.py`. The model can only *request* a function call. The hardcoded Python execution scripts act as a rigid firewall, verifying and sanitizing parameters before hitting the tables.
* **Algorithmic Fuzzy Matching (`difflib`):** To manage human errors without taxing the LLM's token context, a hybrid approach was chosen. When a user creates a typo (e.g., `"brakepad"`), the initial precise database lookup fails safely. The application then falls back to local mathematical string similarity filtering via `get_close_matches` with a `0.6` similarity threshold. This handles close spelling variations locally and natively before returning a clean match, completely bypassing the need to call an expensive AI parsing engine.
* **Ambiguity Mitigation Guardrails:** LLMs are natively prone to "pleasing the user" through hallucinations when provided vague requests (e.g., *"How many do we have?"*). By introducing an explicit negative-constraint behavioral guardrail inside the system instructions (*"ask a clarifying question instead of guessing"*), the model’s reasoning loops are bound to an explicit discovery path, protecting inventory records from false reporting.

### 4. Engineering Standards & Modern SDK Lifecycle
To ensure compliance with long-term ecosystem support, the application was successfully migrated from the deprecated legacy `google-generativeai` package to the modern **`google-genai` SDK architecture**. By moving to a unified service-oriented framework using `genai.Client` and structured `types.GenerateContentConfig` payloads, the project uses the official enterprise-grade standard for Gemini models, utilizing native automated tool calling and clean multi-turn session streaming.
