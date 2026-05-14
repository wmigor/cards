import os
import flet as ft

from cards.views.cards_view import CardsView
from cards.model import init_database_async
from cards.views.super_memo_view import SuperMemoView


async def main(page: ft.Page):
	def route_changed():
		if len(page.views) > 0 and page.views[-1].route == page.route:
			page.update()
			return
		view = None
		if page.route == "/":
			view = SuperMemoView()
		elif page.route == "/cards":
			view = CardsView()
		# elif page.route.startswith("/details/"):
		# 	card = int(page.route[page.route.rfind("/") + 1:])
		# 	view = DetailsView(card)
		if view:
			page.views.append(view)
			page.update()

	async def view_pop():
		page.views.pop()
		top_view = page.views[-1]
		await page.push_route(top_view.route)

	path = await ft.StoragePaths().get_application_support_directory()
	db_path = os.path.join(path, "cards.sql")
	await init_database_async(db_path if os.path.exists(path) else ":memory:")
	page.views.clear()
	page.on_route_change = route_changed
	page.on_view_pop = view_pop
	route_changed()


if __name__ == '__main__':
	ft.run(main)
