# Login Page (`login_page.dart`)

The `login_page.dart` file contains the `LoginPage` widget, which displays the main login screen of the application.

## UI Components

The UI is designed to match the provided image and includes:

*   The application logo.
*   The application name "Planex".
*   The subtitle "Not all who wander are lost.".
*   Buttons for "Continue with Google", "Continue with Apple", and "Continue with Email".

## Functionality

*   **Continue with Google**: This button initiates the Google Sign-In flow using the `google_sign_in` package. After a successful sign-in, the user's ID token and access token are passed to Supabase's `signInWithIdToken` method to sign the user in.
*   **Continue with Apple**: This button is currently a placeholder and does not implement the Apple Sign-In flow, as requested.
*   **Continue with Email**: This button navigates the user to the email login page (`/email-login`).

## Placeholders

The page uses placeholder images for the logo and icons. These should be replaced with the actual assets in the `assets/images/` directory.
The `_googleSignIn` method in `login_page.dart` contains placeholder values for `webClientId` and `iosClientId`. These should be replaced with the actual client IDs from your Google Cloud project.