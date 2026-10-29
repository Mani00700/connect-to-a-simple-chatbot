# Terminal Chatbot
# A simple chat in the terminal using the Gemini API (free tier).
# It remembers the conversation and keeps running when a request fails.

# Setup:
#   1. pip install -U google-genai
#   2. Create a key in Google AI Studio and save it in the GEMINI_API_KEY
#      environment variable (never write the key in the code).
#   3. Run: python chatbot.py

# Type "quit" or "exit" to leave.
# Note: model names and SDK details change over time, so check the
# official Gemini docs if something stops working.

from google import genai
from google.genai import errors
import httpx

# client_ok tells the loop below whether the client started correctly
client_ok = True

# The id of the last successful reply. Sending it with the next message is
# what gives the bot its memory (the API itself remembers nothing between calls).
# It starts as None because there is no earlier message yet.
pre_id = None

try:
    client = genai.Client()   # reads GEMINI_API_KEY from the environment
except ValueError as e:
    # No key was found, so we can't chat. Explain the fix and skip the loop.
    client_ok = False
    print(f"Could not start: {e}")
    print("Check that GEMINI_API_KEY is set, then fully close and reopen VS Code.")

# Main chat loop: runs until the user quits (break) or the client failed to start
while client_ok:
    try:
        # .strip() removes spaces around what the user typed
        user_input = input("> ").strip()

        # .lower() makes the check work for "quit", "Quit", "EXIT", etc.
        if user_input.lower() in ("quit", "exit"):
            break

        # Ignore empty input instead of sending it to the API
        if not user_input:
            continue

        # Send the message together with the id of the previous reply,
        # so the model knows the earlier conversation
        interaction = client.interactions.create(
            model = "gemini-3.5-flash-lite",
            input = user_input,
            previous_interaction_id= pre_id
        )

        # These lines only run if the request succeeded. If it fails, an
        # exception skips them and pre_id keeps its last good value, so the
        # conversation can continue from where it was.
        pre_id = interaction.id
        print(interaction.output_text)

    # The except blocks below are checked from top to bottom, so specific
    # errors come first and the general ones come last.

    # Ctrl+C or Ctrl+Z: leave cleanly instead of showing an error
    except (KeyboardInterrupt, EOFError):
        print("\nBye!")
        break
    except errors.ClientError as e:
        # 4xx: you did something the API rejected (bad key, bad model, rate limit)
        if e.code == 429:
            print("Rate limit reached (free tier). Wait a bit, or try again later if you've used up the daily quota.")
        # Some key problems are reported with 401/403, others only mention
        # the key in the message, so we check both
        elif e.code in (401, 403) or "api key" in str(e.message).lower():
            print("Your API key looks invalid. Check GEMINI_API_KEY, then fully close and reopen VS Code.")
        else:
            # Any other rejected request: show the real code and message
            print(f"The request was rejected ({e.code}): {e.message}")
    except errors.ServerError as e:
        # 5xx: the problem is on Google's side
        print(f"Google's server had a problem ({e.code}). Try again in a moment.")
    # Timeout must come before HTTPError, because it is a more specific kind
    except httpx.TimeoutException:
        print("The request timed out. Check your connection and try again.")
    except httpx.HTTPError:
        # Catch-all for network failures, such as Wi-Fi being off
        print("Could not reach Google. Check your internet connection.")
    except Exception as e:
        # Last resort: show what happened instead of crashing the chat.
        # This must stay last, because it matches almost any error.
        print(f"Unexpected error ({type(e).__name__}): {e}")
