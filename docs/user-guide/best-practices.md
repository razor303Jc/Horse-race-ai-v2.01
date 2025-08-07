# 🎯 Best Practices & Pro Tips

Master the Horse Racing AI v2.0 system with these proven strategies and professional techniques.

## 🏆 Prediction Strategy

### Understanding Confidence Scores

The AI system provides confidence scores (0-1) for each prediction. Use these strategically:

!!! success "High Confidence (0.8+)"

    - **Strategy**: Primary betting opportunities
    - **Risk**: Lower, but still present
    - **Action**: Consider larger stakes or exotic bets
    - **Typical Accuracy**: 75-85%

!!! warning "Medium Confidence (0.6-0.8)"

    - **Strategy**: Secondary opportunities
    - **Risk**: Moderate
    - **Action**: Standard bet sizing, avoid exotics
    - **Typical Accuracy**: 60-70%

!!! danger "Low Confidence (<0.6)"

    - **Strategy**: Avoid or minimal exposure
    - **Risk**: High
    - **Action**: Pass or very small exploratory bets
    - **Typical Accuracy**: 40-55%

### Model Ensemble Analysis

The system uses multiple models. Pay attention to:

1. **Consensus Predictions**: When all models agree, confidence is higher
2. **Model Disagreement**: Indicates uncertainty - proceed with caution
3. **Historical Performance**: Check which models perform best at specific tracks

## 📊 Data Analysis Techniques

### Track-Specific Patterns

Different tracks have unique characteristics:

```python
# Example: Analyze track-specific model performance
track_performance = {
    'Flemington': {'win_rate': 65.2, 'confidence_threshold': 0.75},
    'Randwick': {'win_rate': 58.9, 'confidence_threshold': 0.80},
    'Caulfield': {'win_rate': 62.1, 'confidence_threshold': 0.78}
}
```

**Pro Tips:**

- Adjust confidence thresholds per track
- Consider track conditions (firm, good, soft, heavy)
- Weather impact varies by track layout

### Distance Analysis

Horse performance varies significantly by distance:

- **Sprints (1000-1400m)**: Speed and early pace crucial
- **Miles (1400-1800m)**: Balance of speed and stamina
- **Staying (1800m+)**: Stamina and late pace essential

### Form Cycle Recognition

Identify when horses are:

- **Peaking**: Recent improved performances
- **Declining**: Consistent downward trend
- **Fresh**: First run after a break
- **Consistent**: Reliable performance level

## 💰 Bankroll Management

### The 1-3-5 System

Adjust bet sizing based on confidence:

| Confidence | Bet Size       | Risk Level      |
| ---------- | -------------- | --------------- |
| 0.85+      | 5% of bankroll | High conviction |
| 0.75-0.84  | 3% of bankroll | Standard bet    |
| 0.65-0.74  | 1% of bankroll | Speculative     |
| <0.65      | 0% of bankroll | Pass            |

### Kelly Criterion Application

For advanced users, implement Kelly Criterion:

```python
def kelly_bet_size(probability, odds, bankroll):
    """
    Calculate optimal bet size using Kelly Criterion
    """
    decimal_odds = odds  # e.g., 3.50
    edge = (probability * decimal_odds) - 1

    if edge > 0:
        fraction = edge / (decimal_odds - 1)
        return min(fraction * bankroll, 0.05 * bankroll)  # Cap at 5%
    return 0
```

### The 20/80 Strategy (NEW!)

!!! tip "20/80 Strategy - Balanced Win/Place Approach"

    **Concept**: Split stakes with 20% on win market, 80% on place market

    **Best For**:
    - Horses with strong place prospects but uncertain wins
    - Higher place probability than win probability
    - Medium to high confidence AI predictions

    **Example**: $100 total stake = $20 win + $80 place

**When to Use 20/80 Strategy:**

| Scenario  | Win Prob | Place Prob | Confidence | Action                   |
| --------- | -------- | ---------- | ---------- | ------------------------ |
| **Ideal** | 20-35%   | 65-80%     | >75%       | ✅ Use 20/80             |
| **Good**  | 25-40%   | 60-75%     | >70%       | ✅ Consider 20/80        |
| **Avoid** | >40%     | <60%       | <70%       | ❌ Use standard strategy |

**20/80 Strategy Calculator:**

```python
def calculate_twenty_eighty(total_stake, win_odds, place_odds,
                           win_prob, place_prob):
    """
    Calculate 20/80 strategy returns
    """
    win_stake = total_stake * 0.20
    place_stake = total_stake * 0.80

    win_return = win_stake * win_odds
    place_return = place_stake * place_odds

    # Expected value calculation
    win_ev = (win_prob * win_return) - win_stake
    place_ev = (place_prob * place_return) - place_stake
    total_ev = win_ev + place_ev

    return {
        'win_stake': win_stake,
        'place_stake': place_stake,
        'expected_value': total_ev,
        'win_scenario': win_return - total_stake,
        'place_scenario': place_return - total_stake
    }
```

**Daily Implementation:**

1. **Identify Top 3 Horses**: Use AI to find best place prospects
2. **Allocate Budget**: Divide daily bankroll by 3 horses
3. **Apply 20/80 Split**: Each horse gets 20% win, 80% place
4. **Monitor Results**: Track performance vs traditional betting

**Advantages:**

- Higher probability of returns through place betting
- Reduced risk compared to win-only betting
- Still captures upside if horse wins
- AI-optimized selection process

**Example Scenario:**

```
Horse: Thunder Strike
Total Stake: $100
Win Stake: $20 @ 4.20 odds = $84 potential return
Place Stake: $80 @ 1.60 odds = $128 potential return

Outcomes:
• Horse WINS: Return $84 (Loss $16, but covered by other selections)
• Horse PLACES: Return $128 (Profit $28)
• Horse fails to place: Loss $100
```

## 🔍 Advanced Analysis

### Correlation Analysis

Identify patterns between variables:

1. **Jockey-Trainer Combinations**: Some partnerships excel
2. **Barrier-Distance Relationships**: Inside barriers better in sprints
3. **Weight-Class Correlations**: Weight impact varies by class
4. **Seasonal Patterns**: Track/weather seasonal variations

### Market Analysis

Compare AI predictions with market odds:

- **Value Opportunities**: AI probability > Market probability
- **Overlay Situations**: When AI is more confident than market
- **Market Efficiency**: Track how often markets are "wrong"

### Multi-Race Strategies

**Quadrella/Pick 4 Approach:**

```python
# Example strategy for multi-race bets
def select_quadrella_horses(race_cards):
    selections = []
    for race in race_cards:
        # Select horses with confidence > 0.7
        confident_horses = [h for h in race.horses if h.confidence > 0.7]
        # If less than 3 confident selections, skip race
        if len(confident_horses) < 3:
            return None
        selections.append(confident_horses[:3])  # Top 3
    return selections
```

## 📈 Performance Tracking

### Key Metrics to Monitor

1. **Strike Rate**: Percentage of winning bets
2. **ROI**: Return on investment
3. **Profit/Loss**: Absolute performance
4. **Average Odds**: Understanding risk/reward
5. **Longest Losing Streak**: Risk management

### Weekly Review Process

**Monday Analysis:**

```
1. Review previous week's results
2. Identify patterns in wins/losses
3. Adjust confidence thresholds if needed
4. Plan upcoming week's targets
```

### Monthly Optimization

- Analyze track-specific performance
- Adjust model weights based on results
- Review bankroll management effectiveness
- Update betting strategies

## 🚨 Risk Management

### Red Flags to Watch

!!! danger "Stop Loss Triggers"

    - Losing streak of 10+ bets
    - Down 20% of bankroll in a week
    - Model accuracy drops below 45%
    - Emotional decision making

### Diversification Strategies

1. **Track Diversification**: Don't focus on single track
2. **Distance Diversification**: Mix sprints and staying races
3. **Bet Type Diversification**: Win, place, exotic bets
4. **Time Diversification**: Spread bets across race days

## 🧠 Psychology & Discipline

### Emotional Control

- **Set Daily Limits**: Maximum bets and losses
- **Take Breaks**: After significant wins or losses
- **Stick to System**: Don't chase losses with bigger bets
- **Celebrate Small Wins**: Maintain positive mindset

### Common Pitfalls to Avoid

1. **Overconfidence**: Even 85% confidence means 15% failure rate
2. **Revenge Betting**: Chasing losses with poor selections
3. **Analysis Paralysis**: Over-thinking simple decisions
4. **Ignoring Bankroll**: Betting beyond means

## 📱 Technology Integration

### NTFY Notification Setup

To receive actual popup alerts (not just web app messages):

!!! warning "Getting Real Popup Notifications"

    **Problem**: Seeing notifications only in NTFY web app, no popups?

    **Solutions**:

    1. **Browser Setup** (Easiest):
        - Go to: https://ntfy.sh/horse-racing-alerts
        - Click bell icon 🔔 and ALLOW notifications
        - Keep tab open or pinned

    2. **Mobile App** (Most Reliable):
        - Download NTFY app from App/Play Store
        - Subscribe to: `horse-racing-alerts`
        - Enable push notifications

    3. **Test Your Setup**:
        ```bash
        python3 test_popup_ntfy.py
        ```

### API Automation

```python
# Automated daily analysis
import schedule
import time

def daily_analysis():
    race_cards = get_race_cards(date='today')
    high_confidence = filter_high_confidence(race_cards)
    send_notification(high_confidence)

schedule.every().day.at("08:00").do(daily_analysis)
```

### Alert Setup

Configure notifications for:

- High confidence opportunities (>0.8)
- Value opportunities (AI probability > Market probability)
- System health alerts
- Daily performance summaries

## 🔧 Customization Tips

### Personal Model Weights

Adjust model importance based on your experience:

```python
personal_weights = {
    'speed_model': 0.3,      # If you focus on speed
    'class_model': 0.25,     # Class analysis
    'form_model': 0.25,      # Recent form
    'track_model': 0.2       # Track-specific factors
}
```

### Custom Filters

Create personal race filters:

```python
def my_race_filter(race):
    return (
        race.field_size >= 8 and          # Minimum field size
        race.track in ['Flemington', 'Randwick'] and  # Preferred tracks
        race.distance >= 1200 and         # Minimum distance
        race.prize_money >= 50000         # Minimum prize money
    )
```

---

**Remember**: These are guidelines, not guarantees. Horse racing involves inherent risk, and no system can predict outcomes with 100% accuracy. Always bet responsibly and within your means.
