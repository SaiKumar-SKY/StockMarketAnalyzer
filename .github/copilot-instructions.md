<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->
- [x] Verify that the copilot-instructions.md file in the .github directory is created.

- [x] Clarify Project Requirements
	<!-- Stock market analysis with MongoDB persistence, sentiment analysis, intraday data, technical indicators -->

- [x] Scaffold the Project
	<!-- Created requirements.txt, smoke_test.py, README.md with complete setup guide -->

- [x] Customize the Project
	<!-- Added MongoDB models, database operations, news fetcher, intraday fetcher, VADER sentiment, technical indicators -->

- [x] Install Required Extensions
	<!-- No extensions required for Python project -->

- [x] Compile the Project
	<!-- Installed all dependencies: pymongo, pydantic, yfinance, nltk, apscheduler -->

- [x] Create and Run Task
	<!-- Created init_db.py for MongoDB initialization, smoke_test.py for verification -->

- [x] Launch the Project
	<!-- Smoke test and all 35 unit tests pass successfully -->

- [x] Ensure Documentation is Complete
	<!-- README.md fully documents setup, MongoDB architecture, database operations, and usage examples -->

- [x] Implement Technical Indicators
	<!-- Added indicator computation module, unit tests, parquet output, modular design -->

# Project Summary

## Technology Stack
- **Database**: MongoDB (local instance at localhost:27017)
- **ORM/Validation**: Pydantic models for all collections
- **Data Sources**: yfinance (free, no rate limits)
- **NLP**: VADER sentiment analysis via NLTK
- **Scheduling**: APScheduler for market hours jobs
- **Python**: 3.11+ with virtual environment (venv)

## Collections (MongoDB)
1. `prices` - Daily OHLCV (unique: ticker+date)
2. `intraday` - 15-min data (unique: ticker+timestamp)
3. `news` - Headlines+sentiment (unique: url)
4. `features_sentiment` - Daily aggregates (unique: ticker+date)
5. `predictions` - Model outputs (unique: ticker+date+model_name)

## Key Modules
- `src/database.py` - Pydantic models + collection initialization
- `src/db_operations.py` - Upsert/query functions (idempotent)
- `src/data_fetcher.py` - Historical price fetching
- `src/intraday_fetcher.py` - 15-min price data
- `src/news_fetcher.py` - Headlines + VADER sentiment
- `src/indicators.py` - Technical analysis indicators computation
- `scripts/init_db.py` - MongoDB setup with indexes
- `scripts/compute_indicators.py` - Indicator computation script
- `scripts/load_data.py` - Load parquet data into MongoDB

## Test Coverage
- 35 unit tests (all passing)
- Database operations (upsert + query patterns)
- Data validation (fetchers)
- News processing & sentiment analysis
- Market hours detection for intraday jobs
- Technical indicators computation and validation

## Performance Targets
- Sub-500ms queries on indexed fields (ticker, date)
- Atomic upserts prevent duplicates
- Unique constraints enforce data integrity

## Next Steps (Future)
- Integrate fetchers with database layer
- Create backup script with timestamp
- Alembic migrations if needed
- Dashboard with Streamlit for visualization
- ML model predictions to `predictions` collection

- If any tools are available to manage the above todo list, use it to track progress through this checklist.
## Execution Guidelines
PROGRESS TRACKING:
- If any tools are available to manage the above todo list, use it to track progress through this checklist.
- After completing each step, mark it complete and add a summary.
- Read current todo list status before starting each new step.

COMMUNICATION RULES:
- Avoid verbose explanations or printing full command outputs.
- If a step is skipped, state that briefly (e.g. "No extensions needed").
- Do not explain project structure unless asked.
- Keep explanations concise and focused.

DEVELOPMENT RULES:
- Use '.' as the working directory unless user specifies otherwise.
- Avoid adding media or external links unless explicitly requested.
- Use placeholders only with a note that they should be replaced.
- Use VS Code API tool only for VS Code extension projects.
- Once the project is created, it is already opened in Visual Studio Code—do not suggest commands to open this project in Visual Studio again.
- If the project setup information has additional rules, follow them strictly.

FOLDER CREATION RULES:
- Always use the current directory as the project root.
- If you are running any terminal commands, use the '.' argument to ensure that the current working directory is used ALWAYS.
- Do not create a new folder unless the user explicitly requests it besides a .vscode folder for a tasks.json file.
- If any of the scaffolding commands mention that the folder name is not correct, let the user know to create a new folder with the correct name and then reopen it again in vscode.

EXTENSION INSTALLATION RULES:
- Only install extension specified by the get_project_setup_info tool. DO NOT INSTALL any other extensions.

PROJECT CONTENT RULES:
- If the user has not specified project details, assume they want a "Hello World" project as a starting point.
- Avoid adding links of any type (URLs, files, folders, etc.) or integrations that are not explicitly required.
- Avoid generating images, videos, or any other media files unless explicitly requested.
- If you need to use any media assets as placeholders, let the user know that these are placeholders and should be replaced with the actual assets later.
- Ensure all generated components serve a clear purpose within the user's requested workflow.
- If a feature is assumed but not confirmed, prompt the user for clarification before including it.
- If you are working on a VS Code extension, use the VS Code API tool with a query to find relevant VS Code API references and samples related to that query.

TASK COMPLETION RULES:
- Your task is complete when:
  - Project is successfully scaffolded and compiled without errors
  - copilot-instructions.md file in the .github directory exists in the project
  - README.md file exists and is up to date
  - User is provided with clear instructions to debug/launch the project

Before starting a new task in the above plan, update progress in the plan.