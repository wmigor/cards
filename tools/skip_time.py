import os

import flet as ft
import sys

from peewee import fn

from cards.model import init_database_async, Card


async def main(_):
	path = await ft.StoragePaths().get_application_support_directory()
	db_path = os.path.join(path, "cards.sql")
	await init_database_async(db_path if os.path.exists(path) else ":memory:")
	query = Card.update(access=fn.datetime(Card.access, "-1 day"))
	query.execute()
	sys.exit(1)


if __name__ == '__main__':
	ft.run(main)
