import enum


class FormattedIntEnum(enum.IntEnum):
    def __str__(self):
        return self.name.replace("_", " ").title()
