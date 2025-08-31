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
  bool _showFinishedButton = false;

  final String _systemMessage = """
You are a fun, witty AI guide for NYC Vibes, an app that pulls fresh recommendations from Instagram Reels and TikTok based on real-time trends and your location in NYC. Your goal is to skip boring forms and build a quick user profile through a chill, playful chat. Keep it light, emoji-filled, and super casual—like texting a cool friend. Ask one question at a time, wait for their reply, then build on it naturally. Aim for short, few-word answers from them (e.g., "Pick one: low, mid, or high?"). Cover these exact topics in this order, but weave them in conversationally without listing them out:

1. Age
2. General interests (foodie, nightlife, outdoors, shopping, art, or user's own words)
3. Budget range (low, mid, high)
4. Gender
5. Cultural interests (museums, history, architecture, religious sites)
6. Political alignment (progressive, traditional, balanced mix, or none)
7. Drinking habits (party, casual, heavy, sober curious, no thanks)
8. Introvert/extrovert
9. Dietary restrictions

Once you have all info, summarize their profile playfully (e.g., "Gotcha: 25-year-old foodie, mid-budget gal into progressive vibes, extrovert with a casual drink style—no gluten!"), confirm if it's spot on, then call the `showFinishedButton` tool. From there, use their profile + location to query Reels/TikTok for personalized, fresh recs via RAG and time series.

Stay in character: Energetic, non-pushy, fun. If they skip or say "idk," suggest defaults or move on with "No worries, we can tweak later!" Never ask more than needed; keep chat to 9-10 turns max. End onboarding seamlessly into the main query flow.
""";

  @override
  void initState() {
    super.initState();
    _addMessage("Hey! To tailor NYC spots just for you, what's your age? (Just a number or range, like 20s) 😎", 'Claire');
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
      final chatHistory = _messages.map((m) {
        return OpenAIChatCompletionChoiceMessageModel(
          content: [
            OpenAIChatCompletionChoiceMessageContentItemModel.text(m['content']!),
          ],
          role: m['sender'] == 'user' ? OpenAIChatMessageRole.user : OpenAIChatMessageRole.assistant,
        );
      }).toList();

      final chatCompletion = await OpenAI.instance.chat.create(
        model: 'openai/gpt-oss-20b',
        messages: [
          OpenAIChatCompletionChoiceMessageModel(
            content: [
              OpenAIChatCompletionChoiceMessageContentItemModel.text(_systemMessage),
            ],
            role: OpenAIChatMessageRole.system,
          ),
          ...chatHistory,
        ],
        tools: [
          OpenAIToolModel(
            type: 'function',
            function: OpenAIFunctionModel.withParameters(
              name: 'showFinishedButton',
              description: 'Call this tool when you feel you have gotten enough information about the user to build a complete profile.',
              parameters: [],
            ),
          )
        ],
      );

      final response = chatCompletion.choices.first.message;
      if (response.toolCalls != null && response.toolCalls!.isNotEmpty) {
        for (final toolCall in response.toolCalls!) {
          if (toolCall.function.name == 'showFinishedButton') {
            setState(() {
              _showFinishedButton = true;
            });
          }
        }
      } else {
        _addMessage(response.content?.first.text ?? 'Sorry, I could not process that.', 'Claire');
      }
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
        title: const Text('NYC Vibes Onboarding'),
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
          if (_showFinishedButton || _messages.length > 20)
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
