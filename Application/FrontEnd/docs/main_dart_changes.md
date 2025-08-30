# `main.dart` Changes

The `main.dart` file was updated to integrate the new authentication flow and pages.

## Key Changes

1.  **Imports**: The new pages (`splash_page.dart`, `login_page.dart`, `email_login_page.dart`, `home_page.dart`) are imported.
2.  **Theme**: A dark theme is applied to the `MaterialApp` to match the design of the login page.
3.  **Routing**:
    *   The `initialRoute` is set to `/`.
    *   Named routes are defined for all the new pages: `/`, `/login`, `/email-login`, and `/home`.
    *   The `SplashPage` is set as the widget for the initial route (`/`), which handles the initial authentication check and redirection.