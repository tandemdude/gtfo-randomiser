import enum


class FormattedIntEnum(enum.IntEnum):
    def __str__(self):
        return self.name.replace("_", " ").title()


class Primary(FormattedIntEnum):
    AUTOPISTOL = 1
    PISTOL = 2
    HEL_REVOLVER = 3
    DMR = 4
    SMG = 5
    CARBINE = 6
    ASSAULT_RIFLE = 7
    HEAVY_ASSAULT_RIFLE = 8
    MACHINEPISTOL = 9
    HEAVY_SMG = 10
    DOUBLE_TAP_RIFLE = 11
    BURST_RIFLE = 12


class Special(FormattedIntEnum):
    SHOTGUN = 1
    CHOKE_MOD_SHOTGUN = 2
    COMBAT_SHOTGUN = 3
    SNIPER = 4
    BURST_CANNON = 5
    MACHINEGUN = 6
    REVOLVER = 7
    HEL_GUN = 8
    HEL_RIFLE = 9


class Utility(FormattedIntEnum):
    BIOTRACKER = 1
    C_FOAM_LAUNCHER = 2
    AUTO_SENTRY = 3
    BURST_SENTRY = 4
    SNIPER_SENTRY = 5
    MINE_DEPLOYER = 6


class Melee(FormattedIntEnum):
    SLEDGEHAMMER = 1
    MAUL = 2
    MALLET = 3
    GAVEL = 4


class Stage(FormattedIntEnum):
    A1 = 1
    A2 = 2
    A3 = 3
    B1 = 4
    B2 = 5
    B3 = 6
    C1 = 7
    C2 = 8
    C3 = 9
    D1 = 10
    D2 = 11
    E1 = 12


class Difficulty(FormattedIntEnum):
    HIGH = 1
    EXTREME = 2
    OVERLOAD = 3
    PRISONER_EFFICIENCY = 4
