# Finam v0.1.1-alpha

**Release Date:** August 1, 2026

> **⚠️ ALPHA WARNING: Read Before Using**
>
> This is an early alpha release intended for testing and development purposes only. While most core features are present in the UI, **many systems are highly unstable**. You *will* experience unwanted behaviors, application crashes, softlocks, and incomplete processes.
>
> *Please do not use this version to store sensitive or critical financial data, as local database corruption is possible.*

## Changes in this version

*   Changelog is now included in the source code.
*   Update README.md to represent more accurate information about the app's current state.
*   Update build scripts to reduce unnecessary files in the build output.
*   Rename some variables for better clarity.
*   Fix crash when clicking analyzing purchase button.
*   Fix lesson player return button not working, causing the app to softlock.
*   Use correct page transition for all platforms (previously used "Cupertino", which was the default for iOS devices on all platforms).
*   Slightly improve performance.

##  Known Issues & Instability

*   Certain actions may cause softlocks or crashes.
*   The Purchase Scanner AI hasn't been fully implemented.
*   Lessons aren't loaded properly.
*   Fallback page is completely blank, causing the app to softlock.
*   Settings (gear icon) button redirect to settings page, which doesn't exist.
*   Various UI elements may not scale perfectly on all screen sizes just yet.

# Finam v0.1.0-alpha

**Release Date:** July 31, 2026

> **⚠️ ALPHA WARNING: Read Before Using**
>
> This is an early alpha release intended for testing and development purposes only. While most core features are present in the UI, **many systems are highly unstable**. You *will* experience unwanted behaviors, application crashes, softlocks, and incomplete processes.
>
> *Please do not use this version to store sensitive or critical financial data, as local database corruption is possible.*

## New features in this version

Most foundational features have been merged into this build for early exploration:

*   **Interactive Lessons**: The core lesson player is are implemented.
*   **Savings Tracker**: Monitor and manage your savings goals.
*   **Spending Analysis**: Track and analyze your spending patterns.
*   **Purchase Scanner**: Early implementation of the receipt and purchase scanner.
*   **Charts & Analytics**: Initial visual representations of your financial data.
*   **Local Database**: SQLite data persistence is functional for offline use.
*   **Responsive UI**: The mobile-first design is live.

##  Known Issues & Instability

*   Certain actions may cause softlocks or crashes.
*   The Purchase Scanner AI hasn't been fully implemented
*   Various UI elements may not scale perfectly on all screen sizes just yet.