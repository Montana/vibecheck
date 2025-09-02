#!/usr/bin/env python3
import argparse,json,math,re
from collections import defaultdict,Counter
from dataclasses import dataclass
from datetime import datetime,timedelta
from statistics import mean,pstdev
from typing import Dict,List,Tuple,Optional
import calendar
weights={"sentiment":0.35,"emoji":0.15,"hashtags":0.10,"cadence":0.10,"engagement":0.15,"time_of_day":0.10,"platform_signal":0.05}
positive_words=set("amazing awesome great good fantastic wonderful lovely grateful thankful progress proud win winning excited happy joy joyful relieved calm peace balanced energized bloom thriving celebrate celebration love beautiful perfect incredible outstanding excellent brilliant marvelous splendid delightful charming pleasant satisfying fulfilling inspiring motivating uplifting encouraging supportive success achievement accomplishment breakthrough milestone victory triumph success story growth development improvement advancement innovation creativity passion enthusiasm optimism hope blessed fortunate lucky privileged honored humbled touched moved inspired motivated determined focused confident strong resilient brave courageous authentic genuine real".split())
negative_words=set("sad tired exhausted lonely annoyed angry frustrated upset sick ill anxious stressed overwhelmed meh bored hopeless awful terrible worst cry crying mad furious rage broken hurt heartbroken depressed miserable devastated crushed defeated discouraged disheartened disappointed disillusioned betrayed abandoned rejected isolated alienated misunderstood ignored neglected worried concerned scared frightened terrified panicked nervous jittery restless agitated irritable cranky grumpy moody bitter resentful jealous envious spiteful vengeful pain suffering agony torment torture misery despair desolation emptiness void darkness shadow cloud storm chaos confusion disorder mess disaster catastrophe failure".split())
context_positive={"work":{"promotion","raise","bonus","recognition","achievement","success","team","collaboration","innovation"},"social":{"party","celebration","friends","family","love","romance","date","relationship","marriage"},"health":{"fitness","workout","healthy","wellness","meditation","yoga","running","gym","nutrition"},"creative":{"art","music","writing","design","inspiration","muse","creative","artistic","expression"}}
context_negative={"work":{"layoff","fired","demotion","deadline","pressure","stress","overtime","burnout","conflict"},"social":{"breakup","divorce","argument","fight","betrayal","gossip","drama","conflict","rejection"},"health":{"sick","illness","injury","pain","fatigue","exhaustion","stress","anxiety","depression"},"creative":{"block","stuck","uninspired","criticism","rejection","failure","doubt","insecurity"}}
emoji_pos={"😊","😁","😄","😇","😍","🥰","🤗","👍","✨","🌟","🎉","🔥","💯","🌞","☀️","🍰","🍀","🥳","😎","🤩","🥺","😌","🤗","💪","🎯","🏆","💎","🌈","🦋","🌺","🌸"}
emoji_neg={"😞","😢","😭","😡","😠","🤬","💔","🙄","😮‍💨","😴","🥱","🤒","🤕","☔","🌧️","🖤","😰","😨","😱","😵","🤢","🤮","😷","🤧","💀","👻","😈","👿"}
hashtag_pos={"#blessed","#grateful","#selfcare","#wins","#goodvibes","#greatday","#weekendvibes","#vacay","#glowup","#motivation","#inspiration","#success","#love","#happiness","#blessings","#thankful","#positivevibes","#goodlife","#livingmybestlife","#goals","#achievement"}
hashtag_neg={"#mondayblues","#roughday","#burnout","#tired","#fml","#fail","#worstday","#drained","#alone","#stress","#anxiety","#depression","#sad","#lonely","#heartbroken","#overwhelmed","#exhausted","#struggling","#hardtimes","#badday"}
optimal_hours={"monday":[9,10,11,14,15,16],"tuesday":[9,10,11,14,15,16],"wednesday":[9,10,11,14,15,16],"thursday":[9,10,11,14,15,16],"friday":[9,10,11,14,15,16,17,18],"saturday":[10,11,12,14,15,16,17,18,19,20],"sunday":[10,11,12,14,15,16,17,18,19,20]}
platform_weights={"twitter":{"likes":0.4,"comments":0.6,"retweets":0.8},"instagram":{"likes":0.6,"comments":0.8,"shares":0.7},"facebook":{"likes":0.5,"comments":0.7,"shares":0.6},"linkedin":{"likes":0.3,"comments":0.9,"shares":0.8},"tiktok":{"likes":0.5,"comments":0.6,"shares":0.9}}
golden_hours_prior=list(range(10,13))+list(range(18,22))

@dataclass
class Post:
 platform:str
 timestamp:datetime
 text:str
 likes:int
 comments:int
 shares:int=0
 retweets:int=0
@dataclass
class ContactRecommendation:
 best_day:str
 best_hours:List[Tuple[str,str]]
 confidence_score:float
 urgency_level:str
 mood_context:str
 reasoning:str
@dataclass
class MoodAnalysis:
 overall_score:float
 sentiment_trend:str
 engagement_pattern:str
 optimal_contact_times:List[Tuple[str,str]]
 mood_volatility:float
 social_energy:str

def parse_posts(path):
 with open(path,"r",encoding="utf-8") as f:raw=json.load(f)
 posts=[]
 for p in raw:
  ts=datetime.fromisoformat(p["timestamp"])
  platform=p.get("platform","other").lower()
  likes=int(p.get("likes",0))
  comments=int(p.get("comments",0))
  shares=int(p.get("shares",0))
  retweets=int(p.get("retweets",0))
  posts.append(Post(platform,ts,p.get("text",""),likes,comments,shares,retweets))
 posts.sort(key=lambda x:x.timestamp)
 return posts
def tokenize(text):return re.findall(r"[a-zA-Z']+",text.lower())
def extract_hashtags(text):return [h.lower() for h in re.findall(r"#\w+",text)]
def extract_emojis(text):return [ch for ch in text if ord(ch)>1000]
def day_key(dt):return dt.strftime("%Y-%m-%d")
def hour(dt):return dt.hour
def day_of_week(dt):return calendar.day_name[dt.weekday()].lower()
def zscore(x,mu,sigma):return 0.0 if sigma<=1e-9 else (x-mu)/sigma
def clamp01(x):return max(0.0,min(1.0,x))
def logistic(x):return 1/(1+math.exp(-x))
def scale_sym(x,m):
 if x>=m:return 1.0
 if x<=-m:return 0.0
 return 0.5+0.5*(x/m)
def analyze_context(text):
 text_lower=text.lower()
 context_scores={}
 for context,words in context_positive.items():
  pos_count=sum(1 for word in words if word in text_lower)
  neg_count=sum(1 for word in context_negative.get(context,set()) if word in text_lower)
  context_scores[context]=pos_count-neg_count
 return context_scores
def calculate_engagement_score(post,platform_weights):
 weights=platform_weights.get(post.platform,{"likes":0.5,"comments":0.5,"shares":0.5})
 max_likes=max(1,post.likes)
 max_comments=max(1,post.comments)
 max_shares=max(1,post.shares)
 max_retweets=max(1,post.retweets)
 score=(weights.get("likes",0.5)*(post.likes/max_likes)+weights.get("comments",0.5)*(post.comments/max_comments)+weights.get("shares",0.5)*(post.shares/max_shares)+weights.get("retweets",0.5)*(post.retweets/max_retweets))
 return clamp01(score)

class EnhancedFeatureExtractor:
 def __init__(self,posts):
  self.posts=posts
  self.platform_weights=platform_weights
 def per_day_features(self):
  by_day=defaultdict(list)
  for p in self.posts:
   by_day[day_key(p.timestamp)].append(p)
  likes_all=[p.likes for p in self.posts if p.likes is not None]
  comments_all=[p.comments for p in self.posts if p.comments is not None]
  shares_all=[p.shares for p in self.posts if p.shares is not None]
  likes_mu,likes_sd=(mean(likes_all),pstdev(likes_all)) if likes_all else (0,1)
  com_mu,com_sd=(mean(comments_all),pstdev(comments_all)) if comments_all else (0,1)
  shares_mu,shares_sd=(mean(shares_all),pstdev(shares_all)) if shares_all else (0,1)
  hour_pos_counter=Counter()
  hour_total_counter=Counter()
  daily={}
  for d,plist in by_day.items():
   words_pos=words_neg=emo_pos=emo_neg=tag_pos=tag_neg=0
   total_likes=total_comments=total_shares=total_retweets=0
   context_scores=defaultdict(int)
   for p in plist:
    toks=tokenize(p.text)
    words_pos+=sum(1 for t in toks if t in positive_words)
    words_neg+=sum(1 for t in toks if t in negative_words)
    tags=extract_hashtags(p.text)
    tag_pos+=sum(1 for t in tags if t in hashtag_pos)
    tag_neg+=sum(1 for t in tags if t in hashtag_neg)
    emos=extract_emojis(p.text)
    emo_pos+=sum(1 for e in emos if e in emoji_pos)
    emo_neg+=sum(1 for e in emos if e in emoji_neg)
    total_likes+=p.likes
    total_comments+=p.comments
    total_shares+=p.shares
    total_retweets+=p.retweets
    post_context=analyze_context(p.text)
    for context,score in post_context.items():
     context_scores[context]+=score
    h=hour(p.timestamp)
    pos_signal=(sum(1 for t in toks if t in positive_words)+sum(1 for t in tags if t in hashtag_pos)+sum(1 for e in emos if e in emoji_pos))
    neg_signal=(sum(1 for t in toks if t in negative_words)+sum(1 for t in tags if t in hashtag_neg)+sum(1 for e in emos if e in emoji_neg))
    hour_total_counter[h]+=1
    if pos_signal-neg_signal>0:hour_pos_counter[h]+=1
   likes_z=zscore(total_likes,likes_mu,likes_sd)
   com_z=zscore(total_comments,com_mu,com_sd)
   shares_z=zscore(total_shares,shares_mu,shares_sd)
   sentiment_score=scale_sym(words_pos-words_neg,10)
   emoji_score=scale_sym(emo_pos-emo_neg,5)
   hashtag_score=scale_sym(tag_pos-tag_neg,5)
   platform_engagement=0
   for p in plist:
    platform_engagement+=calculate_engagement_score(p,self.platform_weights)
   platform_engagement=clamp01(platform_engagement/len(plist)) if plist else 0.5
   context_score=0
   if context_scores:
    context_score=clamp01(mean(context_scores.values())/5)
   daily[d]={"posts":len(plist),"sentiment":sentiment_score,"emoji":emoji_score,"hashtags":hashtag_score,"engagement":platform_engagement,"context":context_score,"cadence":0.0,"time_of_day":0.0}
  days_sorted=sorted(daily.keys())
  for i,d in enumerate(days_sorted):
   count_today=daily[d]["posts"]
   prev=days_sorted[max(0,i-7):i]
   if prev:
    avg_prev=mean(daily[p]["posts"] for p in prev)
    daily[d]["cadence"]=clamp01(logistic(count_today-avg_prev))
   else:
    daily[d]["cadence"]=0.5
  golden_score={}
  for h in range(24):
   pos=hour_pos_counter[h]
   tot=hour_total_counter[h]
   prior=0.15 if h in golden_hours_prior else 0.0
   frac=(pos/tot) if tot else 0.0
   golden_score[h]=frac+prior
  for d,plist in by_day.items():
   if not plist:
    daily[d]["time_of_day"]=0.5
    continue
   gh=mean(golden_score.get(hour(p.timestamp),0.0) for p in plist)
   daily[d]["time_of_day"]=clamp01(gh)
  return daily,golden_score
class ContactTimingAnalyzer:
 def __init__(self,daily_features,golden_hours):
  self.daily=daily_features
  self.golden_hours=golden_hours
  self.days_sorted=sorted(self.daily.keys())
 def analyze_mood_trends(self,days_back=30):
  recent_days=self.days_sorted[-days_back:] if len(self.days_sorted)>=days_back else self.days_sorted
  if not recent_days:
   return {"trend":"insufficient_data","volatility":0.0,"consistency":0.0}
  mood_scores=[]
  for day in recent_days:
   f=self.daily[day]
   mood_score=(0.4*f["sentiment"]+0.3*f["emoji"]+0.2*f["hashtags"]+0.1*f["context"])
   mood_scores.append(mood_score)
  if len(mood_scores)<2:
   return {"trend":"insufficient_data","volatility":0.0,"consistency":0.0}
  trend_slope=(mood_scores[-1]-mood_scores[0])/len(mood_scores)
  if trend_slope>0.05:
   trend="improving"
  elif trend_slope<-0.05:
   trend="declining"
  else:
   trend="stable"
  volatility=pstdev(mood_scores) if len(mood_scores)>1 else 0.0
  consistency=1.0-volatility
  return {"trend":trend,"volatility":volatility,"consistency":consistency,"recent_avg":mean(mood_scores[-7:]) if len(mood_scores)>=7 else mean(mood_scores)}
 def find_optimal_contact_times(self,target_date=None):
  if not target_date:
   target_date=datetime.now().strftime("%Y-%m-%d")
  target_dt=datetime.strptime(target_date,"%Y-%m-%d")
  day_of_week_name=day_of_week(target_dt)
  optimal_hours_day=optimal_hours.get(day_of_week_name,[9,10,11,14,15,16])
  scored_hours=[]
  for hour in optimal_hours_day:
   golden_score=self.golden_hours.get(hour,0.0)
   scored_hours.append((hour,golden_score))
  scored_hours.sort(key=lambda x:x[1],reverse=True)
  top_hours=scored_hours[:3]
  time_windows=[]
  for hour,score in top_hours:
   start=f"{hour:02d}:00"
   end=f"{min(hour+1,23):02d}:{'30' if hour<23 else '45'}"
   time_windows.append((start,end))
  return time_windows
 def calculate_contact_urgency(self,target_date=None):
  if not target_date:
   target_date=datetime.now().strftime("%Y-%m-%d")
  if target_date not in self.daily:
   return "unknown",0.0,"No data available for this date"
  day_data=self.daily[target_date]
  negative_indicators=0
  if day_data["sentiment"]<0.3:
   negative_indicators+=1
  if day_data["emoji"]<0.3:
   negative_indicators+=1
  if day_data["hashtags"]<0.3:
   negative_indicators+=1
  recent_engagement=day_data["engagement"]
  if recent_engagement<0.3:
   negative_indicators+=1
  if negative_indicators>=3:
   urgency="high"
   urgency_score=0.9
   reasoning="Multiple negative mood indicators detected"
  elif negative_indicators>=2:
   urgency="medium"
   urgency_score=0.7
   reasoning="Some concerning mood signals detected"
  elif negative_indicators>=1:
   urgency="low"
   urgency_score=0.5
   reasoning="Minor mood fluctuations detected"
  else:
   urgency="minimal"
   urgency_score=0.2
   reasoning="Positive mood indicators present"
  return urgency,urgency_score,reasoning
 def generate_contact_recommendation(self,target_date=None):
  if not target_date:
   target_date=datetime.now().strftime("%Y-%m-%d")
  best_hours=self.find_optimal_contact_times(target_date)
  urgency_level,urgency_score,reasoning=self.calculate_contact_urgency(target_date)
  mood_trends=self.analyze_mood_trends()
  confidence_score=0.0
  if target_date in self.daily:
   day_data=self.daily[target_date]
   confidence_score=(0.3*day_data["sentiment"]+0.2*day_data["emoji"]+0.2*day_data["hashtags"]+0.2*day_data["engagement"]+0.1*(1.0-mood_trends["volatility"]))
  if target_date in self.daily:
   day_data=self.daily[target_date]
   if day_data["sentiment"]>0.7:
    mood_context="very positive"
   elif day_data["sentiment"]>0.5:
    mood_context="positive"
   elif day_data["sentiment"]>0.3:
    mood_context="neutral"
   else:
    mood_context="negative"
  else:
   mood_context="unknown"
  return ContactRecommendation(
            best_day=target_date,
            best_hours=best_hours,
            confidence_score=confidence_score,
            urgency_level=urgency_level,
            mood_context=mood_context,
            reasoning=reasoning
        )

class EnhancedDayScorer:
    def __init__(self, daily_feats):
        self.daily = daily_feats
        self.days_sorted = sorted(self.daily.keys())
    
    def rolling_baseline(self, k=7):
        mood_idx = {}
        for d in self.days_sorted:
            f = self.daily[d]
            mood_idx[d] = (0.4 * f["sentiment"] + 0.3 * f["emoji"] + 
                          0.2 * f["hashtags"] + 0.1 * f["context"])
        
        baseline = {}
        for i, d in enumerate(self.days_sorted):
            prev = self.days_sorted[max(0, i-k):i]
            baseline[d] = mean(mood_idx[p] for p in prev) if prev else 0.5
        
        return baseline, mood_idx
    
    def score_day(self, day):
        f = self.daily.get(day)
        if not f:
            return (50.0, 0.5)
        
        baseline, mood_idx = self.rolling_baseline()
        delta = mood_idx[day] - baseline.get(day, 0.5)
        
        curr = 0.0
        curr += WEIGHTS["sentiment"] * f["sentiment"]
        curr += WEIGHTS["emoji"] * f["emoji"]
        curr += WEIGHTS["hashtags"] * f["hashtags"]
        curr += WEIGHTS["cadence"] * f["cadence"]
        curr += WEIGHTS["engagement"] * f["engagement"]
        curr += WEIGHTS["time_of_day"] * f["time_of_day"]
        curr += 0.20 * (0.5 + 0.8 * delta)
        
        prob = clamp01(logistic(3.0 * (curr - 0.6)))
        score = round(100.0 * prob, 1)
        
        return score, prob

def suggest_hours(golden, posts, top_k=3):
    by_hour = Counter(hour(p.timestamp) for p in posts)
    hours = list(range(24))
    max_count = max(by_hour.values()) if by_hour else 1
    
    ranked = sorted(hours, key=lambda h: (golden.get(h, 0.0) - (by_hour.get(h, 0) / max_count) * 0.4), reverse=True)
    picks = ranked[:top_k]
    windows = []
    
    for h in picks:
        start = f"{h:02d}:00"
        end = f"{min(h+1, 23):02d}:{'30' if h < 23 else '45'}"
        windows.append((start, end))
    
    return windows

def run(input_path, target_date, verbose, analyze_contact=False):
    posts = parse_posts(input_path)
    fx = EnhancedFeatureExtractor(posts)
    daily, golden = fx.per_day_features()
    
    today = target_date if target_date else day_key((posts[-1].timestamp if posts else datetime.now()))
    
    scorer=EnhancedDayScorer(daily)
    score, prob = scorer.score_day(today)
    windows = suggest_hours(golden, posts, top_k=3)
    
    print("=== VIBECHECK ANALYSIS ===")
    print(f"Date: {today}")
    print(f"Reachability Score: {score}/100")
    print(f"Probability: {round(prob, 2)}")
    
    if windows:
        print("\nSuggested contact windows:")
        for s, e in windows:
            print(f"  {s} – {e}")
    else:
        print("\nSuggested contact windows: none")
    
    if analyze_contact:
        print("\n=== CONTACT TIMING ANALYSIS ===")
        contact_analyzer = ContactTimingAnalyzer(daily, golden)
        recommendation = contact_analyzer.generate_contact_recommendation(today)
        
        print(f"Best contact day: {recommendation.best_day}")
        print(f"Optimal hours: {', '.join([f'{s}-{e}' for s, e in recommendation.best_hours])}")
        print(f"Confidence: {recommendation.confidence_score:.2f}")
        print(f"Urgency: {recommendation.urgency_level}")
        print(f"Mood context: {recommendation.mood_context}")
        print(f"Reasoning: {recommendation.reasoning}")
        
        trends = contact_analyzer.analyze_mood_trends()
        print(f"\nMood trends (last 30 days):")
        print(f"  Trend: {trends['trend']}")
        print(f"  Volatility: {trends['volatility']:.2f}")
        print(f"  Consistency: {trends['consistency']:.2f}")
        print(f"  Recent average: {trends['recent_avg']:.2f}")
    
    if verbose:
        print("\n=== DETAILED ANALYSIS ===")
        f = daily.get(today)
        if f:
            for k in ["sentiment", "emoji", "hashtags", "cadence", "engagement", "time_of_day", "context"]:
                if k in f:
                    print(f"{k}: {f[k]:.3f}")
        
        print(f"\nTop 8 golden hours:")
        for h, g in sorted(golden.items(), key=lambda x: x[1], reverse=True)[:8]:
            print(f"  {h:02d}:00: {g:.3f}")

def main():
    ap = argparse.ArgumentParser(description="Enhanced social media mood analyzer with contact timing recommendations")
    ap.add_argument("--input", required=True, help="Path to JSON file with social media posts")
    ap.add_argument("--date", help="Target date for analysis (YYYY-MM-DD format)")
    ap.add_argument("--verbose", action="store_true", help="Show detailed analysis")
    ap.add_argument("--contact", action="store_true", help="Analyze optimal contact timing")
    
    args = ap.parse_args()
    run(args.input, args.date, args.verbose, args.contact)

if __name__ == "__main__":
    main()
