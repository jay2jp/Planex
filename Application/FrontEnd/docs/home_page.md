# Home Page (`home_page.dart`)

The `home_page.dart` file contains the `HomePage` widget, which is displayed after a user successfully logs in.

## UI Components

The page displays:

*   A welcome message with the user's email address.
*   A "Logout" button.

## Functionality

*   **Logout**: This button signs the user out of the application using `Supabase.instance.client.auth.signOut()` and redirects them to the login page.