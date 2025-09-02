# vibecheck 

<img width="500" height="500" alt="Title (14)" src="https://github.com/user-attachments/assets/1c15486d-bec3-4afe-a111-2b272b39dd40" />

a lightweight python tool that analyzes mood signals from social media posts (words, emojis, hashtags, engagement) to estimate the best day and time to reach out to someone.

## features

- **advanced sentiment analysis**: context-aware positive/negative word detection
- **multi-platform support**: twitter, instagram, facebook, linkedin, tiktok
- **emoji & hashtag analysis**: comprehensive mood signal extraction
- **contact timing recommendations**: optimal hours based on mood patterns
- **urgency scoring**: determine how urgently someone should be contacted
- **mood trend analysis**: track mood changes over time
- **platform-specific engagement**: weighted scoring for different social platforms

## feature comparison table

| feature | description | weight | impact |
|---------|-------------|---------|---------|
| **sentiment analysis** | analyzes positive/negative words in post content | 35% | core mood detection |
| **emoji analysis** | processes emoji usage for emotional context | 15% | quick mood indicators |
| **hashtag analysis** | evaluates hashtag sentiment and context | 10% | topic and mood context |
| **posting cadence** | analyzes posting frequency patterns | 10% | activity level signals |
| **engagement metrics** | platform-specific like/comment/share scoring | 15% | social interaction level |
| **time of day** | optimal posting and contact hours | 10% | timing optimization |
| **context detection** | work, social, health, creative categorization | 5% | domain-specific analysis |

## platform support details

| platform | likes weight | comments weight | shares weight | retweets weight | best use case |
|----------|--------------|-----------------|----------------|------------------|---------------|
| **twitter** | 40% | 60% | 0% | 80% | news, quick updates |
| **instagram** | 60% | 80% | 70% | 0% | visual content, stories |
| **facebook** | 50% | 70% | 60% | 0% | personal updates, groups |
| **linkedin** | 30% | 90% | 80% | 0% | professional networking |
| **tiktok** | 50% | 60% | 90% | 0% | entertainment, trends |

## mood signal categories

| category | positive signals | negative signals | context weight |
|----------|------------------|------------------|----------------|
| **work** | promotion, success, team, collaboration | layoff, deadline, stress, burnout | 25% |
| **social** | friends, family, love, celebration | breakup, conflict, rejection, drama | 25% |
| **health** | fitness, wellness, meditation, yoga | illness, pain, fatigue, anxiety | 25% |
| **creative** | inspiration, art, music, design | block, criticism, failure, doubt | 25% |

## contact timing matrix

| day of week | optimal hours | mood sensitivity | contact priority |
|-------------|---------------|------------------|------------------|
| **monday** | 9-11 am, 2-4 pm | high (post-weekend adjustment) | medium |
| **tuesday** | 9-11 am, 2-4 pm | medium (settled into routine) | high |
| **wednesday** | 9-11 am, 2-4 pm | medium (midweek energy) | high |
| **thursday** | 9-11 am, 2-4 pm | medium (pre-weekend anticipation) | high |
| **friday** | 9-11 am, 2-6 pm | low (weekend excitement) | medium |
| **saturday** | 10 am - 8 pm | low (relaxed weekend mood) | low |
| **sunday** | 10 am - 8 pm | medium (pre-monday preparation) | medium |

## urgency scoring system

| urgency level | score range | indicators | recommended action |
|---------------|-------------|------------|-------------------|
| **high** | 0.8-1.0 | 3+ negative signals, low engagement | contact within 24 hours |
| **medium** | 0.6-0.8 | 2 negative signals, moderate concerns | contact within 48 hours |
| **low** | 0.4-0.6 | 1 negative signal, minor fluctuations | contact within a week |
| **minimal** | 0.0-0.4 | positive indicators, stable mood | contact at convenience |

## installation

1. clone or download the files
2. install python 3.7+ if not already installed
3. the tool uses only python standard library modules - no additional installation needed

## usage

### basic analysis
```bash
python vibecheck.py --input sample_posts.json
```

### analyze specific date
```bash
python vibecheck.py --input sample_posts.json --date 2024-01-16
```

### detailed analysis with contact timing
```bash
python vibecheck.py --input sample_posts.json --contact --verbose
```

### command line options
- `--input`: path to json file with social media posts (required)
- `--date`: target date for analysis (yyyy-mm-dd format)
- `--verbose`: show detailed analysis breakdown
- `--contact`: analyze optimal contact timing and urgency

## input format

your json file should contain an array of social media posts with this structure:

```json
[
  {
    "platform": "twitter",
    "timestamp": "2024-01-15t09:30:00",
    "text": "post content with emojis and #hashtags",
    "likes": 45,
    "comments": 12,
    "retweets": 8,
    "shares": 0
  }
]
```

### supported platforms
- `twitter`: uses likes, comments, retweets
- `instagram`: uses likes, comments, shares
- `facebook`: uses likes, comments, shares
- `linkedin`: uses likes, comments, shares
- `tiktok`: uses likes, comments, shares

## output examples

### basic analysis
```
=== vibecheck analysis ===
date: 2024-01-16
reachability score: 78.5/100
probability: 0.79

suggested contact windows:
  10:00 – 10:30
  14:00 – 14:30
  15:00 – 15:30
```

### contact timing analysis
```
=== contact timing analysis ===
best contact day: 2024-01-16
optimal hours: 10:00-10:30, 14:00-14:30, 15:00-15:30
confidence: 0.85
urgency: low
mood context: positive
reasoning: minor mood fluctuations detected

mood trends (last 30 days):
  trend: improving
  volatility: 0.12
  consistency: 0.88
  recent average: 0.76
```

## how it works

1. **text analysis**: analyzes post content for positive/negative words, emojis, and hashtags
2. **context detection**: identifies work, social, health, or creative contexts
3. **engagement scoring**: platform-specific weighting of likes, comments, shares, retweets
4. **time patterns**: analyzes posting frequency and optimal contact hours by day of week
5. **mood trends**: tracks sentiment changes over time to identify patterns
6. **contact recommendations**: combines all signals to suggest optimal contact timing

here's a screenshot of what you should see: 

<img width="664" height="445" alt="Screenshot 2025-09-02 at 3 51 15 PM" src="https://github.com/user-attachments/assets/bf64380b-9cbb-4ecd-8ee2-cee849793d28" />

## context categories

- **work**: promotion, success, team, collaboration, deadlines, stress
- **social**: friends, family, love, parties, breakups, conflicts
- **health**: fitness, wellness, illness, pain, anxiety
- **creative**: art, music, inspiration, creative blocks, criticism

## optimal contact hours

the tool suggests contact times based on:
- **weekdays**: 9-11 am, 2-4 pm (work-friendly hours)
- **weekends**: 10 am - 8 pm (social-friendly hours)
- **mood signals**: adjusts recommendations based on detected mood patterns
- **engagement history**: considers when the person is most active online

## use cases

- **sales & marketing**: time outreach when prospects are in positive moods
- **customer support**: contact customers when they're most receptive
- **personal relationships**: reach out to friends/family at optimal times
- **professional networking**: time messages for better response rates
- **content creation**: post when your audience is most engaged

## sample data

use the included `sample_posts.json` file to test the tool with realistic social media data.

## author

michael mendy (c) 2025. 
