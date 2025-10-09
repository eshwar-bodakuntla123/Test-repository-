KPI: Custom impression value / cost
Algorithm: forge_test (1568810)
[  0  ]   ← editable box beside algorithm

🧠 Here’s what each part means:

Custom impression value / cost → This is the objective/KPI your algorithm is optimizing for.

forge_test (1568810) → This is your custom bidding algorithm name.

0 in the editable box → This is your target value or goal for the KPI.
DV360 uses this number to understand what value per cost you’re aiming for.



---

💡 How this target number works:

For Custom impression value / cost, DV360 interprets it like this:

You’ve defined a “value” per impression inside your script (e.g. score like 0–500 or actual dollar value).

This box is where you tell DV360:

> “I want to maximize Value / Cost above this target.”




👉 If you leave it at 0:

The system will try to maximize total value per cost, but without a strict threshold.

Good for early testing / training phase.


👉 If you set a target (e.g. 300 or a dollar value depending on your scoring method):

DV360 will prioritize impressions that push performance toward or above that threshold.

Essentially it says: “Only aggressively bid if the algorithm score/value helps me reach my goal.”



---

📊 Practical example:

Let’s say your custom bidding algorithm returns:

0 = low value

500 = high value


If you:

Set target = 0 → it tries to maximize total value, bidding proportionally to scores.

Set target = 200 → it focuses more on impressions with score ≥ 200

Set target = 400 → it becomes stricter, bidding mainly on top-quality impressions


✅ Tip: Most advertisers start with 0 during training so the algorithm can explore impressions.
Once it stabilizes (after 1–2 weeks and meets minimum impression requirements), they increase the target to fine-tune performance.


---

🧭 Recommended steps for your case:

1. ✅ Keep KPI = Custom impression value / cost


2. ✅ Select your algorithm forge_test (1568810)


3. ✏️ In the box, enter:

0 if this is a new algorithm still collecting training data

Or a target score (e.g. 200–300) if it’s already trained and you want to focus on high-quality impressions

