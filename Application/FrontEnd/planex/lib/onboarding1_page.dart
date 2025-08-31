import 'package:flutter/material.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:dart_openai/dart_openai.dart';

class Onboarding1Page extends StatefulWidget {
  const Onboarding1Page({super.key});

  @override
  State<Onboarding1Page> createState() => _Onboarding1PageState();
}

class _Onboarding1PageState extends State<Onboarding1Page> {
  final TextEditingController _controller = TextEditingController();
  final List<Map<String, String>> _messages = [];
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _addMessage('Hi! I\'m Claire, your AI assistant. I\'m here to learn about your preferences to help you best.', 'Claire');
    _addMessage('Let\'s start with a quick qualifying question:', 'Claire');
    _addMessage('What kind of destinations are you generally interested in (e.g., Adventure, Relaxation, Culture, Food, etc).', 'Claire');
  }

  void _addMessage(String content, String sender) {
    setState(() {
      _messages.add({'sender': sender, 'content': content});
    });
  }

  Future<void> _sendMessage() async {
    final message = _controller.text;
    if (message.isEmpty) return;

    _addMessage(message, 'user');
    _controller.clear();

    setState(() {
      _isLoading = true;
    });

    try {
      final chatCompletion = await OpenAI.instance.chat.create(
        model: 'openai/gpt-oss-20b',
        messages: [
          OpenAIChatCompletionChoiceMessageModel(
            content: [
              OpenAIChatCompletionChoiceMessageContentItemModel.text(
                'You are Claire, an AI assistant for a travel planning app called Planex. Your goal is to understand the user\'s travel preferences. Keep your responses concise and engaging. Ask clarifying questions to get a better understanding of what the user is looking for. The user said: "$message"',
              ),
            ],
            role: OpenAIChatMessageRole.user,
          ),
        ],
      );

      final response = chatCompletion.choices.first.message.content?.first.text ?? 'Sorry, I could not process that.';
      _addMessage(response, 'Claire');
    } catch (e) {
      _addMessage('Error: ${e.toString()}', 'Claire');
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('The Onboarding Process'),
        backgroundColor: const Color(0xFF2C3E50),
      ),
      backgroundColor: const Color(0xFF2C3E50),
      body: Column(
        children: [
          Expanded(
            child: ListView.builder(
              padding: const EdgeInsets.all(16.0),
              itemCount: _messages.length,
              itemBuilder: (context, index) {
                final message = _messages[index];
                final isUser = message['sender'] == 'user';
                return Align(
                  alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
                  child: Container(
                    margin: const EdgeInsets.symmetric(vertical: 4.0),
                    padding: const EdgeInsets.all(12.0),
                    decoration: BoxDecoration(
                      color: isUser ? const Color(0xFF3498DB) : const Color(0xFF34495E),
                      borderRadius: BorderRadius.circular(16.0),
                    ),
                    child: Text(
                      message['content']!,
                      style: const TextStyle(color: Colors.white),
                    ),
                  ),
                );
              },
            ),
          ),
          if (_isLoading)
            const Padding(
              padding: EdgeInsets.all(8.0),
              child: CircularProgressIndicator(),
            ),
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _controller,
                    decoration: InputDecoration(
                      hintText: 'Type here',
                      hintStyle: TextStyle(color: Colors.white.withOpacity(0.5)),
                      filled: true,
                      fillColor: const Color(0xFF34495E),
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(30.0),
                        borderSide: BorderSide.none,
                      ),
                    ),
                    style: const TextStyle(color: Colors.white),
                    onSubmitted: (value) => _sendMessage(),
                  ),
                ),
                const SizedBox(width: 10),
                IconButton(
                  icon: const Icon(Icons.send, color: Colors.white),
                  onPressed: _sendMessage,
                ),
              ],
            ),
          ),
           Padding(
            padding: const EdgeInsets.all(8.0),
            child: ElevatedButton(
              onPressed: () {
                Navigator.of(context).pushReplacementNamed(
                  '/onboarding2',
                  arguments: _messages,
                );
              },
              child: const Text('Finished'),
            ),
          )
        ],
      ),
    );
  }
}
