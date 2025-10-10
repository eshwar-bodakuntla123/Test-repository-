An A/B test for Custom Bidding in Google Display & Video 360 (DV360) is a structured way to measure the real impact of your custom bidding algorithm (e.g., an “Attention-based” strategy) against your current or baseline bidding.

Here’s a clear breakdown of what this test involves 👇


---

🧪 Goal of the A/B Test

To compare performance between:

A: Your new Custom Bidding (CB) algorithm (e.g., Attention-based)

B: Your Original bidding strategy (e.g., manual CPM, tCPA, or tROAS)


This helps determine if the custom algorithm truly drives better performance on your chosen KPI (e.g., attention score, conversions, cost efficiency, engagement).


---

🧭 Step-by-Step A/B Testing Framework

1. Launch Custom Bidding Algorithm

Train and deploy your Attention-based custom bidding algorithm.

Ensure it’s fully trained and eligible for use (no errors, sufficient signals).

Don’t assign it to your existing IO yet — create a new test IO.



---

2. Set Up Experiment

Create two identical insertion orders (IOs):

IO	Bidding	Purpose

IO A	Custom Bidding	Test
IO B	Original strategy (e.g., fixed bid/manual)	Control


✅ Both should have:

Same budget split (e.g., 50/50 or as recommended)

Same targeting (geo, inventory, audience, frequency caps)

Same creatives (or equivalent)


❌ No extra audiences or special targeting in one vs. the other.


---

3. Run for 3–4 Weeks (Minimum)

Recommended minimum flight duration: 3–4 weeks for stable data.

Run both IOs in parallel to eliminate seasonality or external factors.

Limit optimization activity:

❌ Do not make major changes to the Custom Bidding IO during the test.

✅ You can decrease the addressable inventory in the Original IO (e.g., exclude poor-performing sites).

❌ Do not add new inventory to the Original IO.



This ensures clean, comparable results.


---

4. Optimization Guidelines

Original IO: Optimize normally as you would (bid adjustments, exclusions).

Custom Bidding IO: Let the algorithm learn and optimize on its own.

Don’t introduce new signals or campaigns mid-test.

Limit changes to flight dates, targeting, or creatives.



---

5. Evaluate Performance

At the end of the flight:

Metric	Custom Bidding IO	Original IO	Result

Impressions	📊	📊	
CPM / CPC	📊	📊	
Attention / KPI Score	📊	📊	
Conversions / CPA	📊	📊	


Focus on your primary KPI (e.g., attention score, cost efficiency, conversions).

Also check secondary metrics (viewability, CTR, CPM, CPC, spend pacing).

Use DV360’s experiment reporting or a custom dashboard (e.g., Looker Studio or BigQuery exports).



---

6. Decision Making

After reviewing results:

🟢 If Custom Bidding performs better → scale it to more IOs or entire campaigns.

🟡 If results are neutral → consider extending the test or adjusting the signal weights.

🔴 If underperforming → analyze signals, flight settings, and algorithm quality.


> Google’s guidance: “Use your discretion on a case-by-case basis for analyzing results and extending flights.”




---

📝 Pro Tips

Run only one A/B test at a time for clean results.

Avoid overlapping audiences or placements between the two IOs.

Use clear naming conventions for IOs (e.g., Test_Attention_CB vs. Control_Manual).

Document any changes made during the test period.

Export impression and conversion logs for deeper analysis if needed.



---

✅ Summary:
An A/B test for Custom Bidding in DV360 compares algorithm-driven optimization vs. manual or standard bidding in a controlled, parallel setup. Keep the Custom Bidding IO stable, let it learn, and measure against a control to make a data-backed scaling decision.

Would you like me to give you a practical example of setting up such a test with real targeting/budget structure (e.g., video or display campaign)?

