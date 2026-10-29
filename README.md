# Terminal Chatbot

A simple command-line chatbot in Python that uses the Gemini API (free tier).
It remembers the conversation, and it keeps running when a request fails instead of crashing.

## Features

- Chat with a model directly in the terminal
- Remembers earlier messages in the same session
- Type `quit` or `exit` (any capitalization) to leave, or press Ctrl+C
- Ignores empty input
- Handles errors with clear messages: missing or invalid API key, rate limits, rejected requests, server problems, timeouts, and no internet connection
- A failed request never erases the conversation, so you can retry and carry on

## Requirements

- Python 3.9 or newer
- The `google-genai` library
- A free Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey)

```bash
pip install -U google-genai
```

## Setup: API key

The key is read from the `GEMINI_API_KEY` environment variable.
**Never write the key in the code or upload it to GitHub.**

**Windows (PowerShell), for the current window only:**

```powershell
$env:GEMINI_API_KEY="your-key-here"
```

**Windows, saved for future windows:**

```powershell
setx GEMINI_API_KEY "your-key-here"
```

After using `setx`, fully close and reopen your terminal or VS Code. Programs only read environment variables when they start, so an already-open window will not see the new value.

**macOS / Linux:**

```bash
export GEMINI_API_KEY="your-key-here"
```

## Usage

```bash
python chatbot.py
```

Then type your messages after the `>` prompt.

Example (illustrative):

```
> My dog is called Max.
Nice to meet you and Max! ...
> What is the capital of France?
The capital of France is Paris.
> What is my dog called?
Your dog is called Max.
> quit
```

## How the memory works

The API does not remember anything between requests on its own.
Each reply comes with an `id`, and the program sends the id of the last successful reply along with the next message.
This lets the server continue the same conversation, so the bot knows what was said before.

The id is only updated after a request succeeds. If a request fails, the program keeps the last good id, so the conversation can continue from where it stopped once the problem is fixed.

## Error handling

| Situation | What the program does |
|---|---|
| No API key at startup | Prints how to set it and does not start the chat |
| Rate limit (429) | Tells you to wait, or to try again later if the daily quota is used up |
| Invalid key (401/403, or the message mentions the key) | Suggests checking `GEMINI_API_KEY` |
| Any other rejected request | Shows the real error code and message |
| Problem on Google's side (5xx) | Asks you to try again in a moment |
| Timeout | Suggests checking your connection |
| No internet connection | Says it could not reach Google |
| Anything unexpected | Shows the error type and message, and keeps the chat running |

## Notes

- Free tiers have rate limits, and the limits vary by model. You can see yours in Google AI Studio. Daily limits reset at midnight Pacific time.
- Do not send private or sensitive information through a free tier.
- Model names and SDK details change over time. The model is set in `chatbot.py`, so if something stops working, check the current [Gemini API docs](https://ai.google.dev/gemini-api/docs) and update it.

## What I practiced

- Calling a model API from Python with an SDK
- Keeping conversation state between requests
- Reading secrets from environment variables
- Handling specific errors with `try/except`, ordered from specific to general
- Writing a loop that survives failures
