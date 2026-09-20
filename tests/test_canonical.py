import unittest

from deepom.canonical import (
    ALL_SUIT_PERMS,
    burnside_plo4_class_count,
    canonical_key_plo4,
    raw_plo4_hand_count,
)


class CanonicalizationTests(unittest.TestCase):
    def test_raw_hand_count(self):
        self.assertEqual(raw_plo4_hand_count(), 270_725)

    def test_all_24_suit_permutations_collapse_to_same_key(self):
        base = ["As", "Kd", "Qh", "Jc"]
        base_key = canonical_key_plo4(base)
        suits = "cdhs"
        suit_index = {s: i for i, s in enumerate(suits)}
        for perm in ALL_SUIT_PERMS:
            transformed = [
                c[0] + suits[perm[suit_index[c[1]]]]
                for c in base
            ]
            self.assertEqual(canonical_key_plo4(transformed), base_key)

    def test_card_order_does_not_change_key(self):
        a = canonical_key_plo4(["As", "Ks", "Qh", "Jd"])
        b = canonical_key_plo4(["Jd", "Qh", "Ks", "As"])
        self.assertEqual(a, b)

    def test_distinct_suit_structures_do_not_collapse(self):
        rainbow = canonical_key_plo4(["As", "Kd", "Qh", "Jc"])
        double_suited = canonical_key_plo4(["As", "Ks", "Qh", "Jh"])
        self.assertNotEqual(rainbow, double_suited)

    def test_burnside_count(self):
        self.assertEqual(burnside_plo4_class_count(), 16_432)


if __name__ == "__main__":
    unittest.main()
