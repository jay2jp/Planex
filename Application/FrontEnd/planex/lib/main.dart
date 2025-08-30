import 'package:flutter/material.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:planex/splash_page.dart';
import 'package:planex/login_page.dart';
import 'package:planex/email_login_page.dart';
import 'package:planex/home_page.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await dotenv.load(fileName: ".env");
  await Supabase.initialize(
    url: dotenv.env['SUPABASE_URL']!,
    anonKey: dotenv.env['SUPABASE_ANON_KEY']!,
  );
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Planex',
      theme: ThemeData.dark().copyWith(
        primaryColor: const Color(0xFF2C3E50),
        scaffoldBackgroundColor: const Color(0xFF2C3E50),
        colorScheme: const ColorScheme.dark().copyWith(
          primary: const Color(0xFF2C3E50),
          secondary: const Color(0xFF3498DB),
        ),
      ),
      initialRoute: '/',
      routes: {
        '/': (context) => const SplashPage(),
        '/login': (context) => const LoginPage(),
        '/email-login': (context) => const EmailLoginPage(),
        '/home': (context) => const HomePage(),
      },
    );
  }
}