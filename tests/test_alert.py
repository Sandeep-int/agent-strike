from reporter.alert import check_thresholds


def test_no_alerts_within_limits():
    stats = {"miss_rate": 0.03, "fp_rate": 0.01}
    alerts = check_thresholds(stats)
    assert alerts == []


def test_miss_rate_alert():
    stats = {"miss_rate": 0.10, "fp_rate": 0.01}
    alerts = check_thresholds(stats)
    assert any("Miss rate" in a for a in alerts)


def test_fp_rate_alert():
    stats = {"miss_rate": 0.03, "fp_rate": 0.05}
    alerts = check_thresholds(stats)
    assert any("False positive" in a for a in alerts)


def test_both_alerts():
    stats = {"miss_rate": 0.10, "fp_rate": 0.05}
    alerts = check_thresholds(stats)
    assert len(alerts) == 2


def test_exact_threshold_not_alert():
    stats = {"miss_rate": 0.05, "fp_rate": 0.02}
    alerts = check_thresholds(stats)
    assert alerts == []
