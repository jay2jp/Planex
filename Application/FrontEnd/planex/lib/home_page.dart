import 'package:flutter/material.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:dart_openai/dart_openai.dart';

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  final SupabaseClient _supabase = Supabase.instance.client;
  final TextEditingController _controller = TextEditingController();
  final List<Map<String, String>> _messages = [];
  bool _isLoading = false;


  Future<void> _signOut() async {
    try {
      await _supabase.auth.signOut();
    } on AuthException catch (error) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(error.message)),
      );
    } catch (error) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('An unexpected error occurred')),
      );
    }
    if (mounted) {
      Navigator.of(context).pushReplacementNamed('/login');
    }
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
                'You are a helpful travel assistant. The user said: "$message"',
              ),
            ],
            role: OpenAIChatMessageRole.user,
          ),
        ],
      );

      final response = chatCompletion.choices.first.message.content?.first.text ?? 'Sorry, I could not process that.';
      _addMessage(response, 'AI');
    } catch (e) {
      _addMessage('Error: ${e.toString()}', 'AI');
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
        title: const Text('Location: Sohrab'),
        actions: [
          IconButton(
            onPressed: () {
              // TODO: Implement profile functionality
            },
            icon: const Icon(Icons.person_outline),
          ),
        ],
        backgroundColor: const Color(0xFF2C3E50),
      ),
      drawer: Drawer(
        child: ListView(
          padding: EdgeInsets.zero,
          children: [
            DrawerHeader(
              decoration: const BoxDecoration(
                color: Color(0xFF34495E),
              ),
              child: Text(
                'Welcome, ${_supabase.auth.currentUser?.email ?? 'Guest'}',
                style: const TextStyle(color: Colors.white, fontSize: 24),
              ),
            ),
            ListTile(
              leading: const Icon(Icons.logout),
              title: const Text('Logout'),
              onTap: _signOut,
            ),
          ],
        ),
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
            child: Column(
              children: [
                Row(
                  children: [
                    Expanded(
                      child: TextField(
                        controller: _controller,
                        decoration: InputDecoration(
                          hintText: 'Type your message...',
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
                const SizedBox(height: 10),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                  children: [
                    ElevatedButton(onPressed: () {ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Not Implemented Yet')));}, child: const Text('Travel Guides')),
                    ElevatedButton(onPressed: () {ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Not Implemented Yet')));}, child: const Text('Pin Chat')),
                    ElevatedButton(onPressed: () {ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Not Implemented Yet')));}, child: const Text('New Search')),
                    ElevatedButton(onPressed: () {ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Not Implemented Yet')));}, child: const Text('Saved')),
                  ],
                )
              ],
            ),
          ),
        ],
      ),
    );
  }
}
