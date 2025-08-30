# Email Login Page (`email_login_page.dart`)

The `email_login_page.dart` file contains the `EmailLoginPage` widget, which allows users to sign in or sign up using their email and password.

## UI Components

The page includes:

*   A form with text fields for email and password.
*   A "Sign In" button.
*   A "Sign Up" button.

## Functionality

*   **Sign In**: This button uses the entered email and password to sign the user in with Supabase authentication (`signInWithPassword`). On success, the user is redirected to the home page.
*   **Sign Up**: This button uses the entered email and password to sign the user up with Supabase authentication (`signUp`). On success, the user is shown a confirmation message and is expected to verify their email.