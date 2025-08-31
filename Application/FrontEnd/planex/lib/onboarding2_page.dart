import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:dart_openai/dart_openai.dart';

class Onboarding2Page extends StatefulWidget {
  const Onboarding2Page({super.key});

  @override
  State<Onboarding2Page> createState() => _Onboarding2PageState();
}

class _Onboarding2PageState extends State<Onboarding2Page> {
  Future<Map<String, String>>? _summaryFuture;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (_summaryFuture == null) {
      final messages = ModalRoute.of(context)!.settings.arguments as List<Map<String, String>>;
      _summaryFuture = _generateSummary(messages);
    }
  }

  Future<Map<String, String>> _generateSummary(List<Map<String, String>> messages) async {
    try {
      final response = await OpenAI.instance.chat.create(
        model: 'gpt-3.5-turbo',
        responseFormat: {'type': 'json_object'},
        messages: [
          OpenAIChatCompletionChoiceMessageModel(
            content: [
              OpenAIChatCompletionChoiceMessageContentItemModel.text(
                'Based on the following conversation, generate a JSON object with two keys: "title" (a short, catchy title for the user\'s travel persona, e.g., "Solo Adventurer & Cultural Explorer") and "summary" (a brief summary of their travel preferences). The conversation is: ${messages.toString()}',
              ),
            ],
            role: OpenAIChatMessageRole.user,
          ),
        ],
      );

      final content = response.choices.first.message.content?.first.text ?? '{}';
      final decoded = json.decode(content);
      return {
        'title': decoded['title'] ?? 'No Title',
        'summary': decoded['summary'] ?? 'No Summary',
      };
    } catch (e) {
      return {
        'title': 'Error',
        'summary': 'Error generating summary: ${e.toString()}',
      };
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF2C3E50),
      body: SafeArea(
        child: Center(
          child: Padding(
            padding: const EdgeInsets.all(24.0),
            child: FutureBuilder<Map<String, String>>(
              future: _summaryFuture,
              builder: (context, snapshot) {
                if (snapshot.connectionState == ConnectionState.waiting) {
                  return const CircularProgressIndicator();
                } else if (snapshot.hasError) {
                  return Text('Error: ${snapshot.error}', style: const TextStyle(color: Colors.white));
                } else if (snapshot.hasData) {
                  final data = snapshot.data!;
                  return Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      const Text(
                        'YOU ARE A...',
                        style: TextStyle(
                          fontSize: 24,
                          fontWeight: FontWeight.bold,
                          color: Colors.white,
                        ),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        data['title']!,
                        textAlign: TextAlign.center,
                        style: const TextStyle(
                          fontSize: 32,
                          fontWeight: FontWeight.bold,
                          color: Colors.white,
                        ),
                      ),
                      const SizedBox(height: 30),
                      Image.asset(
                        'assets/images/adventure.png',
                        height: 200,
                        errorBuilder: (context, error, stackTrace) => Container(
                          height: 200,
                          width: 300,
                          color: Colors.grey,
                          child: const Center(
                            child: Text('Image Placeholder'),
                          ),
                        ),
                      ),
                      const SizedBox(height: 30),
                      Text(
                        data['summary']!,
                        textAlign: TextAlign.center,
                        style: const TextStyle(
                          fontSize: 16,
                          color: Colors.white70,
                        ),
                      ),
                      const SizedBox(height: 50),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                        children: [
                          TextButton.icon(
                            onPressed: () {
                              Navigator.of(context).pushReplacementNamed('/onboarding1');
                            },
                            icon: const Icon(Icons.chat_bubble_outline, color: Colors.white),
                            label: const Text(
                              'Try Again',
                              style: TextStyle(color: Colors.white),
                            ),
                          ),
                          ElevatedButton(
                            onPressed: () {
                              Navigator.of(context).pushReplacementNamed('/home');
                            },
                            style: ElevatedButton.styleFrom(
                              backgroundColor: const Color(0xFF3498DB),
                              padding: const EdgeInsets.symmetric(horizontal: 40, vertical: 15),
                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(30.0),
                              ),
                            ),
                            child: const Text(
                              'LFG!',
                              style: TextStyle(fontSize: 18),
                            ),
                          ),
                        ],
                      ),
                    ],
                  );
                } else {
                  return const Text('No summary generated.', style: TextStyle(color: Colors.white));
                }
              },
            ),
          ),
        ),
      ),
    );
  }
}
