# Setup Guide

This guide provides the necessary steps to set up and run the application.

## 1. Image Assets

The application uses placeholder images for the logo and icons. Please replace the following files in the `Application/FrontEnd/planex/assets/images/` directory with your actual assets:

*   `logo.png`
*   `google_logo.png`
*   `email_icon.png`

## 2. Environment Variables

Create a `.env` file in the `Application/FrontEnd/planex/` directory with your Supabase project credentials:

```
SUPABASE_URL=YOUR_SUPABASE_URL
SUPABASE_ANON_KEY=YOUR_SUPABASE_ANON_KEY
```

## 3. Google Sign-In Configuration

To enable Google Sign-In, you need to configure it in your Google Cloud Console and Supabase project.

### Google Cloud Console

1.  Go to the [Google Cloud Console](https://console.cloud.google.com/).
2.  Create a new project or select an existing one.
3.  Go to **APIs & Services > Credentials**.
4.  Click **Create Credentials > OAuth client ID**.
5.  Create a client ID for **Web application**. This will be your `webClientId`.
6.  Create a client ID for **iOS**. This will be your `iosClientId`. You will need to provide your app's bundle ID (`com.example.planex`).
7.  For the iOS client ID, you will get a `REVERSED_CLIENT_ID`. You will need this for the iOS configuration.

### Supabase Project

1.  Go to your Supabase project dashboard.
2.  Go to **Authentication > Providers**.
3.  Enable the **Google** provider.
4.  Enter the **Web Client ID** in the `Authorized Client IDs` field.
5.  Turn on the **Skip nonce checks** option.

### iOS Configuration

1.  Open the `ios/Runner/Info.plist` file.
2.  Replace the placeholder `com.googleusercontent.apps.YOUR_REVERSED_IOS_CLIENT_ID` with the `REVERSED_CLIENT_ID` you obtained from your Google Cloud iOS client ID.

### Flutter Code

1.  Open the `lib/login_page.dart` file.
2.  Replace the placeholder values for `webClientId` and `iosClientId` with the client IDs you obtained from the Google Cloud Console.