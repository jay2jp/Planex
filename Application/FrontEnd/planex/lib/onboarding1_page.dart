import 'package:flutter/material.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:dart_openai/dart_openai.dart';
import 'package:flutter_markdown/flutter_markdown.dart';

class Onboarding1Page extends StatefulWidget {
  const Onboarding1Page({super.key});

  @override
  State<Onboarding1Page> createState() => _Onboarding1PageState();
}

class _Onboarding1PageState extends State<Onboarding1Page> {
  final TextEditingController _controller = TextEditingController();
  final List<Map<String, String>> _messages = [];
  final ScrollController _scrollController = ScrollController();
  final String systemPrompt = """
  You are a fun, witty AI guide for NYC Vibes, an app that pulls fresh recommendations from Instagram Reels and TikTok based on real-time trends and your location in NYC. Your goal is to skip boring forms and build a quick user profile through a chill, playful chat. Keep it light, emoji-filled, and super casual—like texting a cool friend. Ask one question at a time, wait for their reply, then build on it naturally. Aim for short, few-word answers from them (e.g., "Pick one: low, mid, or high?"). Cover these exact topics in this order, but weave them in conversationally without listing them out:

Start with age: "Hey! To tailor NYC spots just for you, what's your age? (Just a number or range, like 20s) 😎"
General interests: "Awesome! What are you into? Pick 2-3: foodie, nightlife, outdoors, shopping, art, or your own words!"
Budget range: "Got it! What's your budget vibe? Low (free or cheap fun), mid (good value), or high (ready to splurge)?"
Gender: "Cool, to match spots to your style—are you guy, gal, non-binary, or something else?"
Cultural interests: "Any culture cravings? Like museums, history spots, architecture, or religious sites? Pick what appeals! 🏛️"
Political alignment: "For spotting the coolest hidden gems, do you prefer progressive vibes, traditional spots, a balanced mix, or none of that matters? (No judgment, just personalizing!)"
Drinking habits: "Drinks on the menu? Yes (love a party), casual, heavy, sober curious, or no thanks? 🍹"
Introvert/extrovert: "Social style: Introvert (prefer low-key), extrovert (thrive in crowds), or in between?"
Dietary restrictions: "Food prefs? Vegetarian, vegan, gluten-free, allergies, or anything goes?"

Once you have all info, summarize their profile playfully (e.g., "Gotcha: 25-year-old foodie, mid-budget gal into progressive vibes, extrovert with a casual drink style—no gluten!"), confirm if it's spot on, then say: "Profile locked! Now, what's your NYC spot or vibe question? (e.g., 'Best hidden bars in Soho right now')". From there, use their profile + location to query Reels/TikTok for personalized, fresh recs via RAG and time series.
Stay in character: Energetic, non-pushy, fun. If they skip or say "idk," suggest defaults or move on with "No worries, we can tweak later!" Never ask more than needed; keep chat to 9-10 turns max. End onboarding seamlessly into the main query flow.
""";
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _addMessage('Hi! I\'m Claire, your AI assistant. I\'m here to learn about your preferences to help you best.', 'Claire');
    _addMessage('Let\'s start with a quick qualifying question:', 'Claire');
    _addMessage('To get started what is your name?', 'Claire');
  }

  void _addMessage(String content, String sender) {
    setState(() {
      _messages.add({'sender': sender, 'content': content});
    });
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
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
      List<OpenAIChatCompletionChoiceMessageModel> messages = [
        OpenAIChatCompletionChoiceMessageModel(
          content: [
            OpenAIChatCompletionChoiceMessageContentItemModel.text(systemPrompt),
          ],
          role: OpenAIChatMessageRole.system,
        ),
      ];
      for (var msg in _messages) {
        var role = msg['sender'] == 'user' ? OpenAIChatMessageRole.user : OpenAIChatMessageRole.assistant;
        messages.add(
          OpenAIChatCompletionChoiceMessageModel(
            content: [
            OpenAIChatCompletionChoiceMessageContentItemModel.text(msg['content'] ?? ''),
            ],
            role: role,
          ),
        );
      }
      final chatCompletion = await OpenAI.instance.chat.create(
        model: 'openai/gpt-oss-20b',
        messages: messages,
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
              controller: _scrollController,
              padding: const EdgeInsets.all(16.0),
              itemCount: _messages.length,
              itemBuilder: (context, index) {
                final message = _messages[index];
                final isUser = message['sender'] == 'user';
                final bubble = Container(
                  constraints: BoxConstraints(maxWidth: MediaQuery.of(context).size.width * 0.7),
                  padding: const EdgeInsets.all(12.0),
                  decoration: BoxDecoration(
                    color: isUser ? const Color(0xFF3498DB) : const Color(0xFF34495E),
                    borderRadius: BorderRadius.only(
                      topLeft: const Radius.circular(16.0),
                      topRight: const Radius.circular(16.0),
                      bottomLeft: isUser ? const Radius.circular(16.0) : Radius.zero,
                      bottomRight: isUser ? Radius.zero : const Radius.circular(16.0),
                    ),
                  ),
                  child: Markdown(
                    data: message['content'] ?? '',
                    shrinkWrap: true,
                    styleSheet: MarkdownStyleSheet(
                      p: const TextStyle(color: Colors.white),
                    ),
                  ),
                );

                final avatar = CircleAvatar(
                  backgroundImage: const AssetImage('assets/images/logo.png'),
                  radius: 16,
                );

                return Padding(
                  padding: const EdgeInsets.symmetric(vertical: 4.0),
                  child: Row(
                    mainAxisAlignment: isUser ? MainAxisAlignment.end : MainAxisAlignment.start,
                    crossAxisAlignment: CrossAxisAlignment.end,
                    children: [
                      if (!isUser) ...[avatar, const SizedBox(width: 8)],
                      bubble,
                      if (isUser) ...[const SizedBox(width: 8), avatar],
                    ],
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

  @override
  void dispose() {
    _scrollController.dispose();
    super.dispose();
  }
}
