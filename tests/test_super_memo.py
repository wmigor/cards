import unittest
from datetime import datetime, timedelta
from unittest.async_case import IsolatedAsyncioTestCase

from cards.model import init_database_async
from cards.card_service import CardServiceAsync


class SuperMemoTest(IsolatedAsyncioTestCase):

	async def test_add_card(self):
		await init_database_async(":memory:")
		card = await CardServiceAsync.add("key", "value")
		self.assertEqual(2.5, card.easy_factor)
		self.assertEqual(1.0, card.interval)
		self.assertEqual(0.0, card.success)

	async def test_get_cards_for_repeat(self):
		await init_database_async(":memory:")
		apple = await CardServiceAsync.add("apple", "яблоко")
		orange = await CardServiceAsync.add("orange", "апельсин")
		apple.interval = 1
		apple.access = datetime.now()
		await CardServiceAsync.update(apple)
		orange.interval = 2
		orange.access = datetime.now()
		await CardServiceAsync.update(apple)
		cards = await CardServiceAsync.get_cards_for_repeat()
		self.assertEqual(0, len(cards))
		orange.access -= timedelta(days=1)
		apple.access -= timedelta(days=1)
		await CardServiceAsync.update(apple)
		await CardServiceAsync.update(orange)
		cards = await CardServiceAsync.get_cards_for_repeat()
		self.assertEqual(1, len(cards))
		self.assertEqual("apple", cards[0].key)
		orange.access -= timedelta(days=1)
		apple.access -= timedelta(days=1)
		await CardServiceAsync.update(apple)
		await CardServiceAsync.update(orange)
		cards = await CardServiceAsync.get_cards_for_repeat()
		self.assertEqual(2, len(cards))

	async def test_apply_super_memo_quality_2(self):
		await init_database_async(":memory:")
		card = await CardServiceAsync.add("key", "value")
		card.interval = 16
		card.success = 3
		card.easy_factor = 2.8
		card.update_super_memo_2(2)
		self.assertEqual(0, card.success)
		self.assertEqual(1, card.interval)
		self.assertAlmostEqual(2.48, card.easy_factor, delta=0.1)

	async def test_apply_super_memo_quality_3(self):
		await init_database_async(":memory:")
		card = await CardServiceAsync.add("key", "value")
		card.update_super_memo_2(3)
		self.assertEqual(1, card.success)
		self.assertEqual(1, card.interval)
		self.assertAlmostEqual(2.36, card.easy_factor, delta=0.1)
		card.update_super_memo_2(3)
		self.assertEqual(2, card.success)
		self.assertEqual(6, card.interval)
		self.assertAlmostEqual(2.2, card.easy_factor, delta=0.1)
		card.update_super_memo_2(3)
		self.assertEqual(3, card.success)
		self.assertEqual(13, card.interval)
		self.assertAlmostEqual(2.08, card.easy_factor, delta=0.1)

	async def test_apply_super_memo_quality_4(self):
		await init_database_async(":memory:")
		card = await CardServiceAsync.add("key", "value")
		card.update_super_memo_2(4)
		self.assertEqual(1, card.success)
		self.assertEqual(1, card.interval)
		self.assertAlmostEqual(2.5, card.easy_factor, delta=0.1)
		card.update_super_memo_2(4)
		self.assertEqual(2, card.success)
		self.assertEqual(6, card.interval)
		self.assertAlmostEqual(2.5, card.easy_factor, delta=0.1)
		card.update_super_memo_2(4)
		self.assertEqual(3, card.success)
		self.assertEqual(15, card.interval)
		self.assertAlmostEqual(2.5, card.easy_factor, delta=0.1)

	async def test_apply_super_memo_quality_5(self):
		await init_database_async(":memory:")
		card = await CardServiceAsync.add("key", "value")
		card.update_super_memo_2(5)
		self.assertEqual(1, card.success)
		self.assertEqual(1, card.interval)
		self.assertAlmostEqual(2.6, card.easy_factor, delta=0.1)
		card.update_super_memo_2(5)
		self.assertEqual(2, card.success)
		self.assertEqual(6, card.interval)
		self.assertAlmostEqual(2.7, card.easy_factor, delta=0.1)
		card.update_super_memo_2(5)
		self.assertEqual(3, card.success)
		self.assertEqual(16, card.interval)
		self.assertAlmostEqual(2.8, card.easy_factor, delta=0.1)


if __name__ == '__main__':
	unittest.main()
