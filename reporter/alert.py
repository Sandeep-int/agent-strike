import config

def check_thresholds(stats: dict):
    alerts = []

    if stats["miss_rate"] > config.MISS_RATE_THRESHOLD:
        alerts.append(
            f"ALERT: Miss rate {stats['miss_rate']*100:.1f}% exceeds {config.MISS_RATE_THRESHOLD*100}% threshold"
        )

    if stats["fp_rate"] > config.FP_RATE_THRESHOLD:
        alerts.append(
            f"ALERT: False positive rate {stats['fp_rate']*100:.1f}% exceeds {config.FP_RATE_THRESHOLD*100}% threshold"
        )

    if alerts:
        print("\n" + "="*60)
        for a in alerts:
            print(f"⚠️  {a}")
        print("="*60)
    else:
        print("\n✅ All thresholds within limits")

    return alerts
