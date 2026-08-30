# Finam v0.2.1-alpha

**Release Date:** August 30, 2026

> **⚠️ ALPHA WARNING: Read Before Using**
>
> This is an early alpha release intended for testing and development purposes only. While most core features are present in the UI, **many systems are highly unstable**. You *will* experience unwanted behaviors, application crashes, softlocks, and incomplete processes.
>
> *Please do not use this version to store sensitive or critical financial data, as local database corruption is possible.*

## Changes in this version

*   Soft-added settings page.
*   Moved assets folder back outside of src folder, as the previous change has been proven to be quite a bad decision.
*   Package src.pages.global_components.settings_button was removed, moving SettingsButton to src.pages.global_components.top_navigation_bar package

## Bug fixes in this version

*   Fixed app crashes instantly upon launch.
*   Version metadata gets updated correcly.
*   All pages now initalize only once.
*   Settings button no longer redirects to fallback page.
*   Fixed many minor issues for the previous version.

##  Known Issues & Instability

*   Some actions may cause softlocks or crashes.
*   Lesson player and lesson editor UI haven't been updated to match the format in v0.2.0-alpha, rendering both unusable.
*   The Purchase Scanner AI hasn't been fully implemented.
*   Many actions that supposed to update the page don't do that.
*   Some elements might be obstructed by the operating system.
*   Some transaction features are broken.
*   Various UI elements may not scale perfectly on all screen sizes.

# Finam v0.2.0-alpha

**Release Date:** August 29, 2026

> **⚠️ ALPHA WARNING: Read Before Using**
>
> This is an early alpha release intended for testing and development purposes only. While most core features are present in the UI, **many systems are highly unstable**. You *will* experience unwanted behaviors, application crashes, softlocks, and incomplete processes.
>
> *Please do not use this version to store sensitive or critical financial data, as local database corruption is possible.*

## Features in this version

This version contains the new UI, which has been completely redesigned to be more user-friendly and visually appealing. Many new UI features are included:

*   **Financial Chart**: The chart has been completely redesigned with improved interactivity and visual appeal.
*   **Pages UI**: The pages have been redesigned to be more user-friendly and visually appealing.
*   **Source code documentation**: Many parts of the source code has been documented with docstrings and comments for better understanding and maintainability.
*   **Anti-crash**: Automatically restart application after crashing in most cases.

## Changes in this version

*   Moved assets folder into src folder.
*   Removing data.db from the source code, which was falsely included.
*   Removed auto resize text functionality, as it was not working properly and was unnecessary.
*   Improved error handling and user feedback for various UI elements.

##  Known Issues & Instability

*   Certain actions may cause softlocks or crashes.
*   Lesson page is kinda broken...
*   The Purchase Scanner AI hasn't been fully implemented.
*   Many actions that supposed to update the page don't do that.
*   Some elements might be obstructed by the operating system.
*   Some transaction features are broken.
*   Settings (gear icon) button redirect to settings page, which doesn't exist.
*   Various UI elements may not scale perfectly on all screen sizes.
*   Lesson audio stops working after the first slide.
*   Pages are initialized twice during normal app launch.

# Finam v0.1.3-alpha

**Release Date:** August 4, 2026

> **⚠️ ALPHA WARNING: Read Before Using**
>
> This is an early alpha release intended for testing and development purposes only. While most core features are present in the UI, **many systems are highly unstable**. You *will* experience unwanted behaviors, application crashes, softlocks, and incomplete processes.
>
> *Please do not use this version to store sensitive or critical financial data, as local database corruption is possible.*

## Bug fixes in this version

*   Fix images in lessons not rendering.

##  Known Issues & Instability

*   Certain actions may cause softlocks or crashes.
*   The Purchase Scanner AI hasn't been fully implemented.
*   Settings (gear icon) button redirect to settings page, which doesn't exist.
*   Various UI elements may not scale perfectly on all screen sizes just yet.
*   Lesson audio stops working after the first slide.

# Finam v0.1.2-alpha

**Release Date:** August 3, 2026

> **⚠️ ALPHA WARNING: Read Before Using**
>
> This is an early alpha release intended for testing and development purposes only. While most core features are present in the UI, **many systems are highly unstable**. You *will* experience unwanted behaviors, application crashes, softlocks, and incomplete processes.
>
> *Please do not use this version to store sensitive or critical financial data, as local database corruption is possible.*

## Changes in this version

*   Several syntax and variable name changes for better clarity.
*   Update flet packages version to 0.86.5.
*   Remove unnecessary button in the side menu.

## Bug fixes in this version

*   Fix fallback page, now displaying a message instead of being completely blank.
*   Lessons actually load now, though there are still several bugs related to it.

##  Known Issues & Instability

*   Certain actions may cause softlocks or crashes.
*   The Purchase Scanner AI hasn't been fully implemented.
*   Settings (gear icon) button redirect to settings page, which doesn't exist.
*   Various UI elements may not scale perfectly on all screen sizes just yet.
*   Lesson audio stops working after the first slide.
*   Lesson images are not rendered at all.

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
*   Use correct page transition for all platforms (previously used "Cupertino", which was the default for iOS devices on all platforms).
*   Slightly improve performance.

## Bug fixes in this version

*   Fix crash when clicking analyzing purchase button.
*   Fix lesson player return button not working, causing the app to softlock.

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

## Features in this version

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