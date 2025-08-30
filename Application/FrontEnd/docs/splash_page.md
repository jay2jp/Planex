# Splash Page (`splash_page.dart`)

The `splash_page.dart` file contains the `SplashPage` widget, which is the initial page loaded when the application starts.

## Functionality

The `SplashPage` is a stateful widget that performs the following actions:

1.  **Authentication Check**: It checks if there is an active user session using `Supabase.instance.client.auth.currentSession`.
2.  **Redirection**:
    *   If a session exists, the user is redirected to the home page (`/home`).
    *   If no session exists, the user is redirected to the login page (`/login`).

This page ensures that users who are already logged in are taken directly to the application's home page, while new or logged-out users are prompted to log in.