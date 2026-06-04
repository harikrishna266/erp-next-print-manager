"""Shared, pure pricing helpers.

These functions take plain numbers/lists and return plain values — no Frappe
document or database access — so they can be unit-tested in isolation and
reused by every pricing engine.
"""


def pick_tier_idx(thresholds, value):
	"""Return the index of the largest threshold that is <= value.

	``thresholds`` are the tier breakpoints (e.g. quantity tiers [100, 200, 500]
	or area tiers [0, 10, 100]) and must be sorted ascending. A customer's
	quantity (or computed area) is "bucketed" down to the nearest lower tier.

	Falls back to 0 (the lowest tier) when ``value`` is below every threshold or
	the list is empty.
	"""
	idx = 0
	for i, threshold in enumerate(thresholds):
		if value >= threshold:
			idx = i
	return idx


def _flt(value, default=0.0):
	"""Coerce a value to float, returning ``default`` for None/blank/garbage."""
	try:
		return float(value)
	except (TypeError, ValueError):
		return default


def _price_list_for_side(row, side):
	"""Pick the relevant per-tier price list from a spec's price row.

	Order of preference:
	1. the chosen ``side`` (e.g. "Single Side") if present and non-empty,
	2. a side-independent ``"prices"`` list (used by area rows),
	3. the other side, as a last-resort fallback.
	Returns ``[]`` when nothing usable is found.
	"""
	chosen = row.get(side)
	if isinstance(chosen, list) and chosen:
		return chosen

	prices = row.get("prices")
	if isinstance(prices, list) and prices:
		return prices

	other = "Double Side" if side == "Single Side" else "Single Side"
	other_list = row.get(other)
	if isinstance(other_list, list) and other_list:
		return other_list

	return []


def get_spec_rate(row, side, tier_idx):
	"""Return one spec value's per-unit rate at the given tier and side.

	``row`` is a v2 price row (a dict) — either side-keyed
	(``{"Single Side": [...], "Double Side": [...]}``) or side-independent
	(``{"prices": [...]}``). ``tier_idx`` indexes into the chosen price list and
	is clamped to the last tier when out of range. Returns 0 for a malformed row.

	This is a raw table lookup only — multiplying by area (for Area Based items)
	is the engine's job, not this function's.
	"""
	if not isinstance(row, dict):
		return 0

	prices = _price_list_for_side(row, side)
	if not prices:
		return 0

	if tier_idx < len(prices):
		return _flt(prices[tier_idx])
	return _flt(prices[-1])
