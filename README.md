# Finam - Financial Learning/Management App

A comprehensive financial literacy application built with **Flet** and **Python**, designed to help users learn about budgeting, savings, spending management, and financial planning through interactive lessons and real-time tracking.

## Features

- **Interactive Lessons** - Engaging lessons which helps users have a better understanding on financial management
- **Savings Tracker** - Monitor and manage your savings goals
- **Spending Analysis** - Track and analyze your spending patterns
- **Purchase Scanner** - Scan receipts and track purchases
- **AI Integration** - Powered by Google Generative AI for deep insights
- **Charts & Analytics** - Visual representation of financial data
- **Responsive Design** - Mobile-first UI that works across all platforms
- **Multi-language Support** - Currently supports Vietnamese and English, with more languages coming in the future.
- **Local Database** - SQLite database for offline data persistence

## Prerequisites

- **Python** ≥ 3.14
- **uv** - Python package installer (recommended) or pip

## Installation

### Android (.apk)

1. Navigate to the [Releases](https://github.com/PEKKAMC/Finam/releases) page of this repository.
2. Download the latest `.apk` file to your Android device.
3. Open the downloaded `.apk` file.
4. If prompted, allow your device to install apps from unknown sources:
    * Go to **Settings** > **Apps** > **Special app access** > **Install unknown apps**.
    * Toggle the switch for the browser or file manager you used to download the file.
5. Tap **Install** and wait for the process to finish.
6. Launch the app!

### iOS (.ipa)

Because of Apple's restrictions on sideloading, you can install the iOS version using sideloading tools like [AltStore](https://altstore.io/) or [Sideloadly](https://sideloadly.io/).

1. Navigate to the [Releases](https://github.com/PEKKAMC/Finam/releases) page and download the latest `.ipa` file.
2. Connect your iPhone to your computer and use your preferred sideloading tool to install the `.ipa`.
3. Once installed, trust the developer certificate on your device:
    * Go to **Settings** > **General** > **VPN & Device Management**.
    * Tap on your Apple ID under "Developer App" and select **Trust**.
4. Launch the app!

## Google account authorization

Google sign-in is optional and available from the profile page. The Google account is stored as an app-wide setting, independent of the selected local profile. Financial data continues to stay in the local database and is not synced or backed up by this sign-in feature.

Fill in `assets/google_auth.json` before building. The client ID and backend/redirect URLs are public configuration, not secrets. Native desktop and mobile builds open the system browser and listen locally, so `redirect_url` must use `http://localhost:<port>/oauth_callback` or `http://127.0.0.1:<port>/oauth_callback`. Web builds instead require `https://<app-origin>/oauth_callback` (or the matching local development origin). Register the exact redirect URI with the Google OAuth web client. The configured native callback is `http://localhost:8550/oauth_callback`. Environment variables with the names below override the file when available:

The web callback is kept in server memory while sign-in is pending, so the callback must return to the same running app instance.

The app stores the Firebase refresh token in its local SQLite settings to keep Google sign-in active across launches. Signing out clears this token.

The purchase scanner requires Google sign-in and allows one scan per Google account per UTC day. Its usage card shows the remaining allowance and next reset time.
| Variable                    | Purpose                                                                              |
| :-------------------------- | :----------------------------------------------------------------------------------- |
| `FINAM_BACKEND_URL`         | HTTPS base URL of the Finam backend (defaults to `https://finam-backend.vercel.app`) |
| `GOOGLE_OAUTH_CLIENT_ID`    | Google OAuth web client ID                                                           |
| `GOOGLE_OAUTH_REDIRECT_URL` | Exact callback URI registered for the Google web client                              |

Use the deployed Vercel domain (not the Vercel dashboard URL) for `backend_url`. Configure the matching callback URI and keep the Google client secret and Firebase service-account JSON only in the backend Vercel environment; the backend README lists those server variables.