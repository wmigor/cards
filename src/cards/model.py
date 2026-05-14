import asyncio
from datetime import datetime

from peewee import DatabaseProxy, Model, TextField, FloatField, DateTimeField, SqliteDatabase, \
	AutoField, IntegerField, ForeignKeyField

_database = DatabaseProxy()


class BaseModel(Model):
	class Meta:
		database = _database


class Card(BaseModel):
	card: int = AutoField()
	key: str = TextField()
	value: str = TextField()
	access = DateTimeField(default=datetime.now)
	easy_factor: float = FloatField(default=2.5)
	interval: float = FloatField(default=1.0)
	success: int = IntegerField(default=0)

	def __str__(self):
		return f"{self.key}: {self.value}, success: {self.success}, interval: {self.interval}, easy_factor: {self.easy_factor}, access: {self.access}"

	def get_repeat_remaining_seconds(self) -> int:
		now = datetime.now().timestamp()
		repeat_time = self.access.timestamp() + self.interval * 86400.0
		remaining = repeat_time - now
		return int(max(0, round(remaining)))

	def update_super_memo_2(self, quality: int):
		if quality < 3:
			self.success = 0
			self.interval = 1
		else:
			if self.success == 0:
				self.interval = 1
			elif self.success == 1:
				self.interval = 6
			else:
				self.interval = round(self.interval * self.easy_factor)
			self.success += 1
		self.easy_factor += 0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)
		self.easy_factor = max(1.3, self.easy_factor)
		self.access = datetime.now()


class SuperMemo(BaseModel):
	super_memo: int = AutoField()
	card: int = ForeignKeyField(Card, on_delete="CASCADE")
	repetitions: int = IntegerField(default=0)
	interval: float = FloatField(default=1.0)
	easy_factor: float = FloatField(default=2.5)
	access = DateTimeField(default=datetime.now)

	def apply_quality(self, quality: int):
		if quality < 3:
			self.repetitions = 0
			self.interval = 1
			self.save()
		else:
			if self.repetitions == 0:
				self.interval = 1
			elif self.repetitions == 1:
				self.interval = 6
			else:
				self.interval = round(self.interval * self.easy_factor)
			self.easy_factor += max(1.3, 0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
		self.access = datetime.now()
		self.save()


def init_database(name: str):
	sqlite = SqliteDatabase(name, check_same_thread=False)
	_database.initialize(sqlite)
	sqlite.create_tables([Card, SuperMemo])

	@sqlite.func("LOWER")
	def sqlite_lower(value):
		return value.lower() if value else value


async def init_database_async(name: str):
	return await asyncio.get_running_loop().run_in_executor(None, init_database, name)
