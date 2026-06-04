import unittest

from tdn_print_manager.pricing.calc import get_spec_rate, pick_tier_idx


class TestPickTierIdx(unittest.TestCase):
	TIERS = [100, 200, 300, 400, 500, 750]

	def test_value_between_tiers_buckets_down(self):
		# 350 falls between 300 and 400 -> use the 300 tier (index 2)
		self.assertEqual(pick_tier_idx(self.TIERS, 350), 2)

	def test_value_exactly_on_a_tier(self):
		self.assertEqual(pick_tier_idx(self.TIERS, 100), 0)
		self.assertEqual(pick_tier_idx(self.TIERS, 500), 4)

	def test_value_below_all_uses_lowest_tier(self):
		self.assertEqual(pick_tier_idx(self.TIERS, 50), 0)

	def test_value_above_all_uses_top_tier(self):
		self.assertEqual(pick_tier_idx(self.TIERS, 1000), 5)

	def test_area_tiers_starting_at_zero(self):
		area = [0, 10, 100, 500, 5000]
		self.assertEqual(pick_tier_idx(area, 0), 0)
		self.assertEqual(pick_tier_idx(area, 7), 0)
		self.assertEqual(pick_tier_idx(area, 250), 2)

	def test_empty_thresholds(self):
		self.assertEqual(pick_tier_idx([], 100), 0)


class TestGetSpecRate(unittest.TestCase):
	# A real side-keyed bundle row (300 GSM Artcard) across 6 tiers.
	SIDE_ROW = {
		"Single Side": [0.81, 0.875, 0.83333, 0.81, 0.782, 0.7],
		"Double Side": [1.56, 1.68, 1.5, 1.56, 1.496, 1.333333],
	}
	# A real area row (Standard Flex) — side-independent, per sqft.
	AREA_ROW = {"unit": "per_sqft", "prices": [25, 22, 20, 18, 16]}

	def test_single_side_lookup(self):
		# 300 GSM, single side, 300 tier (index 2) -> 0.83333
		self.assertAlmostEqual(get_spec_rate(self.SIDE_ROW, "Single Side", 2), 0.83333)

	def test_double_side_lookup(self):
		self.assertAlmostEqual(get_spec_rate(self.SIDE_ROW, "Double Side", 0), 1.56)

	def test_tier_out_of_range_clamps_to_last(self):
		self.assertAlmostEqual(get_spec_rate(self.SIDE_ROW, "Single Side", 99), 0.7)

	def test_area_row_ignores_side_uses_prices(self):
		self.assertAlmostEqual(get_spec_rate(self.AREA_ROW, "Single Side", 1), 22)
		self.assertAlmostEqual(get_spec_rate(self.AREA_ROW, "Double Side", 1), 22)

	def test_falls_back_to_other_side_when_chosen_empty(self):
		row = {"Single Side": [], "Double Side": [5, 6]}
		self.assertAlmostEqual(get_spec_rate(row, "Single Side", 0), 5)

	def test_prices_preferred_when_chosen_side_absent(self):
		row = {"prices": [3, 4], "Double Side": [9, 9]}
		self.assertAlmostEqual(get_spec_rate(row, "Single Side", 1), 4)

	def test_malformed_row_returns_zero(self):
		self.assertEqual(get_spec_rate(5, "Single Side", 0), 0)
		self.assertEqual(get_spec_rate({}, "Single Side", 0), 0)


if __name__ == "__main__":
	unittest.main()
