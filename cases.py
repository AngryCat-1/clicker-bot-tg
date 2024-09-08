class InvItems:
    def __init__(self):
        pass


class DefaultBigCactus():
    def __init__(self):
        self.name = "Обычный большой кактус"
        self.description = "С шансом 1/3 дает +2🌵 от клика. Может суммироваться"
        self.chance = 33
        self.boost = 2
        self.rare = "Обычный"
        self.fragment = 3


class ConsantBigCactus():
    def __init__(self):
        self.name = "Постоянный большой кактус"
        self.description = "Дает +1🌵 от клика. Может суммироваться"
        self.chance = 100
        self.boost = 1
        self.rare = "Редкий"
        self.fragment = 5

class CritBigCactus():
    def __init__(self):
        self.name = "Критический большой кактус"
        self.description = "С шансом 1/20 дает +25🌵 от клика. Может суммироваться"
        self.chance = 5
        self.boost = 22
        self.rare = "Эпический"
        self.fragment = 10


class BaseCase:
    items = {DefaultBigCactus:50, CritBigCactus:20, ConsantBigCactus:30}
    min_fragments = 2
    max_fragments = 5


