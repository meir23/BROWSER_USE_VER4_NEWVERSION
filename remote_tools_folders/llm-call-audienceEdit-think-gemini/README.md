# Facebook Ads Manager AI Assistant

This project uses Google's Gemini AI model to analyze screenshots of Facebook Ads Manager and provide step-by-step guidance for configuring lookalike audiences, with integration to OpenAI's Computer Use API for automated actions.

## 🏗️ Project Architecture Overview

The system follows a two-stage pipeline architecture:
1. **Gemini AI Analysis**: Processes screenshots to generate textual instructions
2. **OpenAI Computer Use Integration**: Takes these instructions to execute actions

Key components:
- `llm_caller.py`: Handles Gemini API interactions
- `gemini_to_computer_use.py`: Manages the integration between Gemini and OpenAI
- `utils/logging_utils.py`: Centralizes all logging functionality
- `computer_agent_request.py`: Located in parent directory, handles OpenAI Computer Use API calls

```
                      ┌────────────────────┐
                      │     Screenshot     │
                      └──────────┬─────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────┐
│               Gemini AI (llm_caller.py)             │
│                                                     │
│  ┌─────────────┐   ┌─────────────┐   ┌───────────┐  │
│  │Example Image│   │System Prompt│   │Few Shots   │  │
│  └─────────────┘   └─────────────┘   └───────────┘  │
└────────────────────────────┬────────────────────────┘
                             │
                             ▼
                  ┌────────────────────┐
                  │  Detailed Analysis │
                  └──────────┬─────────┘
                             │
                             ▼
┌────────────────────────────────────────────────────────┐
│         OpenAI Computer Use (via parent dir)           │
└────────────────────────────┬───────────────────────────┘
                             │
                             ▼
                  ┌────────────────────┐
                  │ Automated Actions  │
                  └────────────────────┘
```

## 🔄 Core Workflows

### Main Workflow: Image Analysis to Action
1. User provides a screenshot and optional task description
2. `gemini_to_computer_use.py` orchestrates the process
3. The image is sent to Gemini AI via `llm_caller.py`
4. Gemini analyzes the image using example data and generates detailed instructions
5. These instructions are captured and logged
6. The instructions and image are sent to OpenAI Computer Use API
7. OpenAI suggests concrete actions (e.g., click coordinates)
8. Results from both systems are logged and returned

### Logging Workflow
1. All requests to external APIs are logged before sending
2. All responses are logged upon receipt
3. Integration steps are logged at each point in the process
4. Logs are timestamped and stored in appropriate directories

## 📁 Code Organization Principles

The code follows these organization principles:
- **Separation of Concerns**: Each file has a clear, singular responsibility
- **Utility Extraction**: Common functions are moved to utility modules
- **Consistent Logging**: Extensive logging throughout all operations
- **Standalone Executability**: Main scripts can run independently

Directory structure:
- `/utils`: Contains utility modules (primarily logging)
- `/logs`: Stores API request/response logs
- `/integration_logs`: Stores logs of the integration process
- `/adset_training_images`: Contains example images for Gemini
- `/model_response_few_shots`: Contains example responses for Gemini
- `/test_images`: Contains additional test images

## 🔗 Critical Dependencies

This project requires:
- Python 3.8+
- `google-generativeai`: For Gemini API interactions (matching their SDK version)
- `openai`: For OpenAI API interactions (version compatibility with Computer Use API)
- `python-dotenv`: For environment variable management

Specific version requirements:
```
google-generativeai>=0.5.0  # Required for file upload support
openai>=1.13.0              # Required for Computer Use API
python-dotenv>=1.0.0
```

⚠️ **Version Constraints**: The OpenAI client must be compatible with the Computer Use API, which may have specific version requirements.

## 📝 Logging Philosophy

**Logging is critical to this codebase and should never be reduced.**

Principles:
- **Comprehensive Logging**: Every step of the process must be logged
- **Separation of Log Types**: 
  - `logs/`: API requests and responses to Gemini
  - `integration_logs/`: Integration-specific logs between systems
- **Structured Format**: JSON for structured data, text for responses
- **No Loss of Information**: Complete payloads are always logged
- **Timestamping**: All logs include timestamps in the filename

The `utils/logging_utils.py` module centralizes all logging functionality to keep main code files cleaner while maintaining comprehensive logging capabilities.

## 🚨 Error Handling Conventions

Error handling follows these conventions:
- Log all errors with detailed information
- Return `None` values for failed operations rather than raising exceptions in top-level functions
- Document error conditions in function docstrings
- Check for required files/paths before operations
- Validate inputs early in the process
- Restore system state (e.g., stdout) in finally blocks

## 🔌 Integration Points

Key integration points that must be preserved:
1. **Gemini to Computer Use Bridge**: 
   - In `gemini_to_computer_use.py::process_with_gemini_and_computer_use()`
   - Takes Gemini output and passes it to OpenAI

2. **External File References**:
   - `computer_agent_request.py` from parent directory
   - Example images and response files

3. **Environment Variables**:
   - `GEMINI_API_KEY`
   - `OPENAI_API_KEY`

## 🏷️ Naming Conventions

- **Files**: Snake case for utility files, descriptive names for main files
- **Functions**: 
  - `generate()`: Main Gemini interaction
  - `process_with_gemini_and_computer_use()`: Main integration function
  - `log_*()`: Logging utility functions
- **Variables**:
  - API responses with descriptive names (e.g., `gemini_response`, `computer_use_response`)
  - Constants in UPPER_CASE (e.g., `INTEGRATION_LOG_DIR`)
- **Logs**: Named with function and timestamp (e.g., `gemini_response_20250331_123456.log`)

## 🧪 Test Coverage Requirements

Tests are provided via standalone scripts:
- `test_gemini_to_computer.py`: Tests the full integration
- `test_integration.py`: Tests the integration with OpenAI
- `test_with_new_image.py`: Tests Gemini functionality on new images

When modifying code:
- Run all test scripts to verify functionality
- Check log outputs for expected content
- Ensure test images are properly processed

No formal unit tests are implemented, but test scripts should be maintained to demonstrate functionality.

## ⚡ Performance Considerations

- **Streaming Responses**: Gemini responses are streamed for faster feedback
- **Image Encoding**: OpenAI requires base64 encoding, which can be memory-intensive for large images
- **Stdout Capture**: The current implementation captures stdout, which may not be efficient but preserves complete outputs

## 🚫 Do Not Modify List

These elements should not be modified:
- **Logging Mechanism**: Do not reduce or remove logging functionality
- **Core API Interfaces**: Maintain compatibility with Gemini and OpenAI APIs
- **Example Content**: Do not alter training images or example responses
- **System Prompt**: The system prompt is carefully crafted for specific behaviors

## ⚙️ Configuration Management

Configuration is handled through:
1. **Environment Variables**: API keys stored in environment
2. **Dotenv**: `.env` file support for local development
3. **Hardcoded Paths**: Some paths are hardcoded and need to be preserved

Models and parameters:
- Gemini model: Currently `gemini-2.5-pro-exp-03-25`
- Temperature setting: 0.4 (lower for more consistent outputs)

## 📚 API Documentation

### Gemini API
- Uses file upload capability for image processing
- Requires few-shot examples to guide behavior
- Includes a system prompt for consistent behavior

### OpenAI Computer Use API
- Called via `send_initial_computer_request()` in parent directory
- Requires image and textual instructions
- Returns suggested actions and reasoning

## 🧵 Thread Safety

The code is not specifically designed for multi-threading. Key considerations:
- Global `stdout` manipulation in `gemini_to_computer_use.py`
- Shared log directories that could have conflicts with parallel execution
- No thread locks on shared resources

## 🗄️ State Management

This system is primarily stateless with no persistent state between runs.
Temporary state includes:
- Captured stdout during Gemini API calls
- In-memory API responses before logging

## 🔒 Security Considerations

- **API Keys**: Stored in environment variables, never in code
- **Image Data**: User-provided images are processed but not permanently stored
- **Logging**: Complete API responses are logged, which may include sensitive data

## 🤝 Contribution Guidelines

When contributing to this project:
1. Maintain all logging functionality
2. Keep the separation between Gemini and OpenAI integration
3. Preserve the capability to run each component independently
4. Ensure backwards compatibility with existing scripts
5. Follow the existing code structure and naming conventions
6. Document any changes comprehensively

## ✅ Code Review Checklist

Before submitting changes, verify:
- [ ] All logging is preserved
- [ ] Tests pass successfully
- [ ] Documentation is updated
- [ ] Error handling is consistent
- [ ] Compatibility with existing scripts is maintained
- [ ] Code follows existing structure and conventions

## 🚀 Release Process

To release a new version:
1. Update `requirements.txt` with any new dependencies
2. Test with both Gemini and OpenAI APIs
3. Check all logs for expected outputs
4. Update README.md with any new functionality
5. Ensure backward compatibility

## 🚩 Feature Flag System

No formal feature flag system is implemented. New features should be added in a way that preserves existing functionality.

## ⚠️ Common Pitfalls

Known issues to watch for:
1. **Stdout Capture**: The method used to capture Gemini output is sensitive to changes
2. **Path Resolution**: Ensure relative paths are properly handled, especially for images
3. **OpenAI API Changes**: The Computer Use API is evolving and may have compatibility issues
4. **Log Directory Creation**: Ensure log directories exist before writing
5. **JSON Serialization**: Some objects need special handling for JSON logging

## 🔍 Debugging Guide

When debugging issues:
1. Check the logs in `logs/` and `integration_logs/`
2. Verify API keys are correctly set in environment
3. Ensure all required example files exist
4. Check for changes in API behavior or requirements
5. Test components individually before integration

## 📖 Documentation Standards

Code documentation requirements:
- Module-level docstrings explaining purpose and usage
- Function docstrings with parameters and return values
- Comments for complex operations
- Inline comments for non-obvious code

## 🔄 Backward Compatibility Policy

Changes must maintain compatibility with:
- Existing command-line interfaces
- Directory structure and file locations
- Logging format and location
- API interfaces

## 📊 Data Flow Diagrams

```
[Image] → [llm_caller.py] → [Text Instructions] → [gemini_to_computer_use.py] → [computer_agent_request.py] → [Actions]
   ↓              ↓                    ↓                        ↓                            ↓
 [logs/]        [logs/]        [integration_logs/]      [integration_logs/]          [integration_logs/]
```

Detailed data flow:
1. Image data flows into Gemini AI processing
2. Text instructions flow from Gemini to OpenAI
3. Action suggestions flow from OpenAI to the output
4. Logs are generated at each step

## 🧰 Utility Functions Directory

The `utils/` directory contains:
- `logging_utils.py`: All logging functionality
- `__init__.py`: Package exports for easy imports

Key utilities:
- `log_integration_step()`: Logs integration steps
- `log_request()`: Logs API requests
- `log_response()`: Logs API responses
- `GeminiCapture`: Class for capturing Gemini output
- `capture_stdout()`: Function for capturing stdout

## 🎯 Contribution Priority Areas

Areas that would benefit from improvement:
1. Better stdout capture mechanism for Gemini output
2. More structured logging format for Computer Use requests
3. Enhanced error handling for API failures
4. Improved display of Computer Use response data
5. Additional utility functions for common operations

## 🔀 Cross-Cutting Concerns

Aspects that affect multiple parts of the codebase:
1. **Logging**: Present throughout all operations
2. **Path Resolution**: Critical for finding files and storing logs
3. **Environment Variables**: Used by multiple components
4. **Error Handling**: Consistent across components
5. **Stdout Management**: Used in multiple places for capturing output

## 🔲 System Boundaries

This system is responsible for:
- Processing screenshots of Facebook Ads Manager
- Generating instructions for navigating the interface
- Optionally executing actions via Computer Use API
- Logging all operations

It is NOT responsible for:
- User interface beyond command-line
- Long-term storage of results
- User authentication or authorization
- Actual control of the browser (only suggestions)

## 🧩 Integration Testing Requirements

When testing changes:
1. Run `test_gemini_to_computer.py` to verify full integration
2. Check logs for expected content and format
3. Verify that both Gemini and OpenAI components work correctly
4. Test with different images to ensure robustness
5. Confirm that all logging is working as expected

## 💾 Important Files and Their Roles

- `llm_caller.py`: Core interface to Gemini AI
- `gemini_to_computer_use.py`: Integration orchestrator
- `utils/logging_utils.py`: Logging utilities
- `system_prompt.md`: Critical for guiding Gemini's behavior
- `model_response_few_shots/`: Examples that guide Gemini's outputs
- `adset_training_images/`: Training images for Gemini
- `test_gemini_to_computer.py`: Main test script for the integration

## 🚀 Getting Started for Contributors

1. Set up environment variables:
```
GEMINI_API_KEY=your_gemini_api_key
OPENAI_API_KEY=your_openai_api_key
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run a test to verify setup:
```bash
python test_gemini_to_computer.py
```

4. Review logs to understand the system behavior

5. Make changes following the guidelines in this document