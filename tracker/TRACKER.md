# Cycling Training Check-In Tracker — structure

Build this in Google Sheets, Excel or any spreadsheet. The formulas below work in both. To get coaching on it, paste or upload the latest rows (CSV is fine) into your chat with the coach.

## Daily (one row per day, starts Mon Nov 16 2026)
| Col | Field | Notes |
|---|---|---|
| A | Date | `=A2+1` down the column |
| B | Readiness | formula below |
| C | Sleep (hrs) | |
| D | Sleep quality (1-5) | 5 = best |
| E | HRV (ms) | optional |
| F | Resting HR | optional |
| G | Legs (1-5) | 5 = fresh |
| H | Energy (1-5) | 5 = high |
| I | Stress (1-5) | 5 = most stressed |
| J | Notes | illness, pain, travel |

Readiness (row 2):
```
=IF(COUNT(C2:I2)=0,"",CHOOSE(MIN(2,AND(C2<>"",C2<6.5)+AND(D2<>"",D2<=2)+AND(E2<>"",E2<0.9*AVERAGE(E$2:E$400))+AND(F2<>"",F2>1.07*AVERAGE(F$2:F$400))+AND(G2<>"",G2<=2)+AND(H2<>"",H2<=2)+AND(I2<>"",I2>=4))+1,"🟢 Go","🟡 Go, monitor","🔴 Easy / rest"))
```
Flags: sleep <6.5 h, quality ≤2, HRV >10% below season average, resting HR >7% above season average, legs ≤2, energy ≤2, stress ≥4. 0 = Go, 1 = monitor, 2+ = easy/rest.

## Sessions (one row per ride or lift)
Date | Type (dropdown: Z2 endurance, Long ride, Sweet spot, Threshold, VO2max, Recovery, Strength, Test, Other) | Minutes | RPE (0-10) | Load `=IF(OR(C2="",D2=""),"",C2*D2)` | Completed (Full / Modified / Skipped) | Avg power (W) | TSS | Carbs (g/hr) | Notes

## Weekly (one row per Monday)
- Weekly load: `=SUMIFS(Sessions!E:E,Sessions!A:A,">="&A2,Sessions!A:A,"<"&A2+7)`
- Load vs last week: `=IF(OR(B2=0,B3=0),"",B3/B2-1)`
- Avg sleep: `=IFERROR(AVERAGEIFS(Daily!C:C,Daily!A:A,">="&A2,Daily!A:A,"<"&A2+7),"")`
- Sessions full / modified+skipped: `COUNTIFS` on Sessions!F
- Manual: avg weight (lb), hours available next week, week rating (1-5), notes

## Tests
Date | Test | Result (W) | Body weight (lb) | W/kg `=IF(OR(C2="",D2=""),"",C2/(D2/2.2046))` | Notes
Baseline: FTP 278 W @ 155 lb = 3.95 W/kg (Nov 14 2026, reported).
