# 📊 Batch Analysis Usage Examples

This document shows how to use the `batch_analyze.py` script for processing multiple videos.

## 🚀 Quick Start

### 1. Basic Usage (Built-in URLs)
```bash
# Make sure your server is running first
python app.py

# In another terminal, run batch analysis
python batch_analyze.py
```

### 2. Create Custom URLs File
```bash
# Create a sample URLs file
python batch_analyze.py --create-sample

# Edit the file with your URLs
nano urls_to_analyze.txt

# Process your URLs
python batch_analyze.py --file urls_to_analyze.txt
```

## 📝 Sample URLs File Format

Create a file called `urls_to_analyze.txt`:

```
# Video URLs to analyze (one per line)
# Lines starting with # are comments and will be ignored

# TikTok examples (these work reliably)
https://www.tiktok.com/@tiktok/video/7106594312292453675?is_copy_url=1&is_from_webapp=v1
https://www.tiktok.com/@tiktok/video/7011536772089924869?is_copy_url=1&is_from_webapp=v1

# Add your URLs below:
https://www.tiktok.com/@username/video/1234567890
https://www.instagram.com/reel/ABC123DEF456/
```

## 🔧 Customizing Analysis Prompts

Edit the `ANALYSIS_PROMPTS` list in `batch_analyze.py`:

```python
ANALYSIS_PROMPTS = [
    "What is the main topic or subject of this video?",
    "Describe what you see happening in this video.",
    "What is the overall mood or tone of this video?",
    "List any products, brands, or items mentioned in this video.",
    "What type of content category does this video belong to?",
    "Is this video educational, entertaining, or promotional?",
]
```

## 📊 Expected CSV Output

The script generates `video_analysis_results.csv` with these columns:

| Column | Description | Example |
|--------|-------------|---------|
| `timestamp` | When analysis was done | `2025-01-20T10:30:45.123456` |
| `url` | Original video URL | `https://www.tiktok.com/@tiktok/video/...` |
| `platform` | TikTok or Instagram | `TikTok` |
| `video_id` | Extracted video ID | `7106594312292453675` |
| `prompt` | Analysis question | `What is the main topic...` |
| `status` | success/error/timeout | `success` |
| `result` | Gemini's analysis | `This video discusses...` |
| `duration_seconds` | Processing time | `45.23` |
| `error_message` | Error details if failed | `null` or error text |

## 🎯 Sample Output

```bash
🚀 Batch Video Analysis
==================================================
📹 URLs to process: 2
📝 Prompts per video: 3
📊 Total analyses: 6
💾 Output file: video_analysis_results.csv

✅ Server is responding

🎬 Processing video 1/2: https://www.tiktok.com/@tiktok/video/7106594312292453675
   🔍 Analysis 1/6 (Prompt 1/3)
   📝 Prompt: What is the main topic or subject of this video?...
   ✅ Success (34.5s): This video appears to be about TikTok's platform features...
   
   🔍 Analysis 2/6 (Prompt 2/3)
   📝 Prompt: Describe what you see happening in this video...
   ✅ Success (28.1s): The video shows various scenes of people using...
   💾 Progress saved (2/6)

🎉 Batch analysis complete!
==================================================
📊 Results Summary:
   ✅ Successful analyses: 6
   ❌ Failed analyses: 0
   📈 Success rate: 100.0%
   💾 Results saved to: video_analysis_results.csv
```

## ⚙️ Configuration Options

Edit these variables in `batch_analyze.py`:

```python
# How long to wait for each analysis (5 minutes)
REQUEST_TIMEOUT = 300

# Delay between requests (be nice to servers)
DELAY_BETWEEN_REQUESTS = 2

# Output filename
OUTPUT_CSV = "my_analysis_results.csv"
```

## 🔄 Advanced Usage

### Process Large Batches
For many URLs (50+), consider:
- Increasing delays: `DELAY_BETWEEN_REQUESTS = 5`
- Running during off-peak hours
- Monitoring server performance

### Custom Prompts for Different Video Types
Create different prompt sets for different content:

```python
# For cooking videos
COOKING_PROMPTS = [
    "What ingredients are shown in this video?",
    "What cooking techniques are demonstrated?",
    "What is the final dish being prepared?",
]

# For educational content
EDUCATIONAL_PROMPTS = [
    "What is the main educational topic?",
    "What key facts or tips are shared?",
    "Who is the target audience?",
]
```

## 📈 Performance Tips

1. **Start Small**: Test with 2-3 URLs first
2. **Monitor Progress**: The script saves every 5 analyses
3. **Check Server Resources**: Each analysis uses GPU/memory for Gemini
4. **Use Reliable URLs**: TikTok official account videos work best
5. **Backup Results**: The CSV is updated incrementally

## 🚨 Troubleshooting

### Common Issues:
- **Server not responding**: Start `python app.py` first
- **High timeout rate**: Increase `REQUEST_TIMEOUT`
- **Rate limiting**: Increase `DELAY_BETWEEN_REQUESTS`
- **Memory issues**: Process fewer videos at once

### Check Progress:
```bash
# Monitor the CSV file as it updates
tail -f video_analysis_results.csv

# Count successful analyses
grep "success" video_analysis_results.csv | wc -l
```

## 🎯 Use Cases

### Content Analysis
- Categorize video content types
- Extract product mentions
- Analyze sentiment/mood

### Research Projects
- Study platform trends
- Compare content across creators
- Analyze engagement patterns

### Business Intelligence
- Competitor content analysis
- Brand mention tracking
- Market research insights

---

**Pro Tip**: Start with the built-in working URLs to verify everything works, then gradually add your own URLs for analysis! 