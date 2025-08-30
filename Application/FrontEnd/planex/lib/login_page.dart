import 'dart:async';

import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:flutter/material.dart';
import 'package:google_sign_in/google_sign_in.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'src/web_wrapper.dart' as web;
class LoginPage extends StatefulWidget {
  const LoginPage({super.key});

  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  StreamSubscription<GoogleSignInAuthenticationEvent>?
      _googleSignInSubscription;

  @override
  void initState() {
    super.initState();
    _initializeGoogleSignIn();
  }

  @override
  void dispose() {
    _googleSignInSubscription?.cancel();
    super.dispose();
  }

  void _initializeGoogleSignIn() {
    // Web Client ID that you registered with Google Cloud.
    const webClientId =
        '696250669836-hv8ke9ah06gpl3b6kirgg5mrnve78ddl.apps.googleusercontent.com';

    // iOS Client ID that you registered with Google Cloud.
    const iosClientId = 'YOUR_IOS_CLIENT_ID';

    final GoogleSignIn googleSignIn = GoogleSignIn.instance;
    
    // Initialize with appropriate parameters for each platform
    googleSignIn.initialize(
      clientId: kIsWeb ? webClientId : iosClientId,
      serverClientId: kIsWeb ? null : webClientId,
    ).then((_) {
      _googleSignInSubscription = googleSignIn.authenticationEvents.listen(
        _handleGoogleSignInEvent,
        onError: _handleGoogleSignInError,
      );
    });
  }

  Future<void> _handleGoogleSignInEvent(
      GoogleSignInAuthenticationEvent event) async {
    if (event is! GoogleSignInAuthenticationEventSignIn) {
      return;
    }

    final googleUser = event.user;
    if (googleUser == null) {
      return; // User cancelled the sign-in
    }

    try {
      final client = googleUser.authorizationClient;
      final authz = await client.authorizationForScopes(['email', 'profile']);
      final accessToken = authz?.accessToken;
      final idToken = googleUser.authentication.idToken;

      if (accessToken == null) {
        throw 'No Access Token found.';
      }
      if (idToken == null) {
        throw 'No ID Token found.';
      }

      await Supabase.instance.client.auth.signInWithIdToken(
        provider: OAuthProvider.google,
        idToken: idToken,
        accessToken: accessToken,
      );

      if (mounted) {
        Navigator.of(context).pushReplacementNamed('/home');
      }
    } catch (error) {
      _showError('Google sign-in failed: $error');
    }
  }

  void _handleGoogleSignInError(Object error) {
    _showError('Google sign-in error: $error');
  }

  Future<void> _triggerGoogleSignIn() async {
    try {
      // For web, we check if the platform supports authenticate
      if (kIsWeb) {
        if (GoogleSignIn.instance.supportsAuthenticate()) {
          await GoogleSignIn.instance.authenticate();
        } else {
          // On web, if authenticate is not supported, we rely on the button click
          // The authentication events listener will handle the sign-in
          _showError('Please click the Google Sign-In button directly');
        }
      } else {
        // For mobile platforms
        if (GoogleSignIn.instance.supportsAuthenticate()) {
          await GoogleSignIn.instance.authenticate();
        } else {
          _showError('Platform does not support Google Sign-In');
        }
      }
    } on GoogleSignInException catch (error) {
      _showError('Google sign-in failed: ${error.code}');
    } catch (error) {
      _showError('Google sign-in failed: $error');
    }
  }

  void _showError(String message) {
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(message)),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF2C3E50),
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.symmetric(horizontal: 24.0),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              crossAxisAlignment: CrossAxisAlignment.center,
              children: [
                // TODO: Replace 'assets/images/logo.png' with your actual logo image.
                // This is a placeholder.
                Image.asset(
                  'assets/images/logo.png',
                  height: 150,
                  errorBuilder: (context, error, stackTrace) => const Icon(
                      Icons.explore,
                      size: 150,
                      color: Colors.white),
                ),
                const SizedBox(height: 20),
                const Text(
                  'Planex',
                  style: TextStyle(
                    fontSize: 48,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
                const SizedBox(height: 10),
                const Text(
                  'Not all who wander are lost.',
                  style: TextStyle(
                    fontSize: 18,
                    color: Colors.white70,
                  ),
                ),
                const SizedBox(height: 50),
                const Text(
                  'Start with',
                  style: TextStyle(
                    fontSize: 16,
                    color: Colors.white70,
                  ),
                ),
                const SizedBox(height: 20),
                // Use the web sign-in button for web platform
                if (kIsWeb) ...[
                  SizedBox(
                    width: double.infinity,
                    height: 50,
                    child: web.renderButton(),
                  ),
                  const SizedBox(height: 15),
                ] else
                  ElevatedButton.icon(
                    onPressed: _triggerGoogleSignIn,
                    // TODO: Replace 'assets/images/google_logo.png' with the actual Google logo.
                    icon: Image.asset('assets/images/google_logo.png',
                        height: 24,
                        errorBuilder: (context, error, stackTrace) =>
                            const Icon(Icons.g_mobiledata, color: Colors.black)),
                    label: const Text('Continue with Google'),
                    style: ElevatedButton.styleFrom(
                      foregroundColor: Colors.black,
                      backgroundColor: Colors.white,
                      minimumSize: const Size(double.infinity, 50),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(25),
                      ),
                    ),
                  ),
                const SizedBox(height: 15),
                // Apple sign in is ignored for now as requested.
                ElevatedButton.icon(
                  onPressed: () {
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(
                          content:
                              Text('Apple Sign-In is not implemented yet.')),
                    );
                  },
                  icon: const Icon(Icons.apple, color: Colors.black),
                  label: const Text('Continue with Apple'),
                  style: ElevatedButton.styleFrom(
                    foregroundColor: Colors.black,
                    backgroundColor: Colors.white,
                    minimumSize: const Size(double.infinity, 50),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(25),
                    ),
                  ),
                ),
                const SizedBox(height: 15),
                ElevatedButton.icon(
                  onPressed: () {
                    Navigator.of(context).pushNamed('/email-login');
                  },
                  // TODO: Replace 'assets/images/email_icon.png' with the actual email icon.
                  icon: Image.asset('assets/images/email_icon.png',
                      height: 24,
                      color: Colors.white,
                      errorBuilder: (context, error, stackTrace) =>
                          const Icon(Icons.email, color: Colors.white)),
                  label: const Text('Continue with Email'),
                  style: ElevatedButton.styleFrom(
                    foregroundColor: Colors.white,
                    backgroundColor: const Color(0xFF34495E),
                    minimumSize: const Size(double.infinity, 50),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(25),
                      side: const BorderSide(color: Colors.white),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
