from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User

from random import randrange as rd

# Not database, classes to work the mechanics of the app
class Dice():

    class DiceSides():
        D2 = 2
        D4 = 4
        D6 = 6
        D8 = 8
        D10 = 10
        D12 = 12
        D20 = 20

    def __init__(self, quantity: int, sides: int) -> None:
        self.quantity = quantity
        self.sides = sides

    def roll(self) -> dict[str, int]:
        rolls = [rd(1, self.sides + 1) for _ in range(self.quantity)]
        total = sum(rolls)
        result = {f"roll_{index + 1}": value for index, value in enumerate(rolls)}
        return result | {"total": total}

    def __str__(self) -> str:
        return f"{self.quantity}d{self.sides}"

    def __repr__(self) -> str:
        return f"Dice({self.quantity, self.sides})"


# Models for the construction of character background
class School(models.Model):
    school_ID = models.CharField(
        verbose_name="School ID",
        db_column="SchoolID",
        max_length=3,
        null=False,
        blank=False,
        primary_key=True
        )
    name = models.CharField(
        verbose_name="School Name",
        db_column="SchoolName",
        max_length=50,
        null=False,
        blank=False
        )

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"[{self.school_ID}]: {self.name}"

class Race(models.Model):
    race_ID = models.CharField(
        db_column="RaceID",
        max_length=3,
        primary_key=True
    )
    name = models.CharField(
        db_column="RaceName",
        max_length=20
    )

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"[{self.race_ID}]: {self.name}"

class RaceTrait(models.Model):
    TRAIT_CATEGORY_OPTIONS = (
        ("A", "Ability"),
        ("P", "Penalty")
    )

    name = models.CharField(
        max_length=100
    )
    description = models.TextField()
    category = models.CharField(
        max_length=1,
        choices=TRAIT_CATEGORY_OPTIONS
    )
    race = models.ForeignKey(
        Race, 
        on_delete=models.CASCADE
    )

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"{self.name} ({self.race})"

# Models for path and skills construction
class Aspiration(models.Model):
    aspiration_ID = models.CharField(
        db_column="AspirationID",
        max_length=3,
        primary_key=True
    )
    name = models.CharField(
        db_column="AspirationName",
        max_length=20,
    )

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"[{self.aspiration_ID}]: {self.name}"

class Path(models.Model):

    class Tier(models.IntegerChoices):
        PROVISIONAL = 0
        BASIC = 1
        ADVANCED = 2
        SPECIALIST = 3

    path_ID = models.CharField(
        db_column="PathID",
        max_length=3,
        primary_key=True
    )
    name = models.CharField(
        db_column="PathName",
        max_length=30        
    )
    tier = models.PositiveSmallIntegerField(
        null=False,
        blank=False,
        default=Tier.BASIC,
        choices=Tier.choices
    )
    requirements = models.JSONField()
    master_bonus = models.CharField(
        db_column="MasterBonus",
        max_length=150
    )
    aspiration = models.ForeignKey(
        Aspiration,
        on_delete=models.DO_NOTHING
    )

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"[{self.path_ID}]: {self.name}"

class Skill(models.Model):

    class Category(models.TextChoices):
        INTRINSIC = "ITS", _("Intrinsic")
        GENERAL = "GEN", _("General")
        SUPPORT = "SUP", _("Support")
        REACTION = "REA", _("Reaction")
        MOVEMENT = "MOV", _("Movement")
        PERFECT = "PER", _("Perfect")

    name = models.CharField(
        db_column="SkillName",
        max_length=100
    )
    description = models.TextField()
    cost = models.PositiveIntegerField()
    _category = models.CharField(
        null=False,
        blank=False,
        max_length=3,
        default=Category.GENERAL,
        choices=Category.choices
    )
    path = models.ForeignKey(
        Path,
        on_delete=models.CASCADE
    )

    @property
    def category(self) -> str:
        return self.Category(self._category).label

    @category.setter
    def category(self, new_category: Category) -> None:
        self._category = new_category

    def __str__(self) -> str:
        return self.name
    
    def __repr__(self) -> str:
        return f"{self.name} ({self.path}, {self.category})"

# Models for the construction of the system mechanics for the character
class Character(models.Model):

    # User that created the character
    player_ID = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='player'
    )

    # Background and physical characteristics
    name = models.CharField(
        max_length=100
    )
    origin = models.CharField(
        max_length=30
    )
    race = models.ForeignKey(
        Race,
        on_delete=models.DO_NOTHING
    )
    school = models.ForeignKey(
        School,
        on_delete=models.DO_NOTHING
    )
    aspiration = models.ForeignKey(
        Aspiration,
        on_delete=models.DO_NOTHING
    )
    weight = models.DecimalField(
        max_digits=6,
        decimal_places=2
    )
    height = models.DecimalField(
        max_digits=5,
        decimal_places=2
    )
    age = models.PositiveSmallIntegerField()

    # Game mechanics information
    level = models.PositiveSmallIntegerField()
    xp_total = models.PositiveIntegerField()
    xp_current = models.PositiveIntegerField()
    hp_total = models.IntegerField()
    hp_current = models.IntegerField()
    hp_temp = models.IntegerField()
    unbalance = models.PositiveIntegerField()
    movement_actions = models.PositiveSmallIntegerField()
    main_actions = models.PositiveSmallIntegerField()
    active_path = models.ForeignKey(
        Path,
        on_delete=models.DO_NOTHING
    )

    # Narrative and other informations
    inventory = models.TextField(blank=True)
    annotations = models.TextField(blank=True)
    coin = models.CharField(
        max_length=200
    )

    def __str__(self) -> str:
        return self.name
    
    def __repr__(self) -> str:
        return f"{self.name} ({self.race}, {self.school})"

class Attribute(models.Model):

    class AttrTypes(models.TextChoices):
        BODY = "C", _("CORPO")
        MIND = "M", _("MENTE")
        FOCUS = "F", _("FOCO")
        SPIRIT = "E", _("ESPÍRITO")
        SOCIAL = "S", _("SOCIAL")
        NATURE = "N", _("NATUREZA")    

    _type = models.CharField(
        max_length=1,
        choices=AttrTypes.choices
    )
    current_value = models.PositiveIntegerField()
    total_value = models.PositiveIntegerField()
    temp_value = models.PositiveIntegerField()
    training_level = models.PositiveSmallIntegerField()
    char_ID = models.ForeignKey(
        Character,
        on_delete=models.CASCADE
    )

    @property
    def type(self) -> str:
        return self.AttrTypes(self._type).label

    @type.setter
    def type(self, new_type: AttrTypes) -> None:
        self._type = new_type

    def __str__(self) -> str:
        return f"{self.type} de {self.char_ID}"

    def __repr__(self) -> str:
        return f"{self.type} {self.current_value} / {self.total_value} [Treino: {self.training_level}]"

    def level_up(self) -> None:
        self.total_value += 1

class Action(models.Model):

    class ActionTypes(models.TextChoices):
        HIT = "A", _("ACERTAR")
        DODGE = "E", _("ESQUIVAR")
        DEFEND = "D", _("DEFENDER")
        RESIST = "R", _("RESISTIR")
        CHANNEL = "C", _("CANALIZAR")

    _type = models.CharField(
        max_length=1,
        choices=ActionTypes.choices
    )
    nd4 = models.PositiveIntegerField()
    nd6 = models.PositiveIntegerField()
    nd8 = models.PositiveIntegerField()
    nd10 = models.PositiveIntegerField()
    nd12 = models.PositiveIntegerField()
    nd20 = models.PositiveIntegerField()
    flat_bonus = models.PositiveIntegerField()
    flat_penalty = models.PositiveIntegerField()
    char_ID = models.ForeignKey(
        Character,
        on_delete=models.CASCADE
    )

    base_dice = Dice.DiceSides.D8

    @property
    def type(self) -> str:
        return self.ActionTypes(self._type).label

    @type.setter
    def type(self, new_type: ActionTypes) -> None:
        self._type = new_type

    def __str__(self) -> str:
        return f"{self.type} para {self.char_ID}"

    def __repr__(self) -> str:
        return f"{self.type} ({self.char_ID})"

    def roll_dice(self) -> dict:
        roll_d4 = Dice(self.nd4, Dice.DiceSides.D4).roll()
        roll_d6 = Dice(self.nd6, Dice.DiceSides.D6).roll()
        roll_d8 = Dice(self.nd8, Dice.DiceSides.D8).roll()
        roll_d10 = Dice(self.nd10, Dice.DiceSides.D10).roll()
        roll_d12 = Dice(self.nd12, Dice.DiceSides.D12).roll()
        roll_d20 = Dice(self.nd20, Dice.DiceSides.D20).roll()
         
        all_rolls = {
            Dice.DiceSides.D4: roll_d4,
            Dice.DiceSides.D6: roll_d6,
            Dice.DiceSides.D8: roll_d8,
            Dice.DiceSides.D10: roll_d10,
            Dice.DiceSides.D12: roll_d12,
            Dice.DiceSides.D20: roll_d20
        }

        total = sum(roll["total"] for roll in all_rolls.values())

        return all_rolls | {"result": total}

    def level_up(self) -> None:
        match self.base_dice:
            case Dice.DiceSides.D4:
                self.nd4 -= 1
                self.nd6 += 1
                self.base_dice = Dice.DiceSides.D6
            case Dice.DiceSides.D6:
                self.nd6 -= 1
                self.nd8 += 1
                self.base_dice = Dice.DiceSides.D8
            case Dice.DiceSides.D8:
                self.nd8 -= 1
                self.nd10 += 1
                self.base_dice = Dice.DiceSides.D10
            case Dice.DiceSides.D10:
                self.nd10 -= 1
                self.nd12 += 1
                self.base_dice = Dice.DiceSides.D12
            case Dice.DiceSides.D12:
                self.nd12 -= 1
                self.nd20 += 1
                self.base_dice = Dice.DiceSides.D20
            case Dice.DiceSides.D20:
                self.nd4 += 1
                self.base_dice = Dice.DiceSides.D4
            case _:
                raise ValueError('There is no dice with these sides')


# Characters can gain access to different paths and skills as they level up
class AvailablePath(models.Model):
    path_ID = models.ForeignKey(
        Path,
        on_delete=models.CASCADE
    )
    current_pp = models.PositiveIntegerField()
    total_pp = models.PositiveIntegerField()
    level = models.PositiveSmallIntegerField()
    is_master = models.BooleanField(default=False)
    char_ID = models.ForeignKey(
        Character,
        on_delete=models.CASCADE
    )

    level_thresholds = {
        0: 1,
        100: 2,
        300: 3,
        500: 4,
        800: 5,
        1100: 6,
        1500: 7,
        2000: 8,
        2500: 9,
        3000: 10
    }

    def __str__(self) -> str:
        return f"{self.path_ID} para {self.char_ID}"

    def __repr__(self) -> str:
        return f"{self.path_ID} ({self.char_ID})"

    def change_total_pp(self, new_pp: int) -> None:
        diff = new_pp - self.total_pp
        self.total_pp = new_pp
        self.current_pp += diff
        
        for pp in self.level_thresholds.keys():
            if (self.total_pp - pp) >= 0:
                self.level = self.level_thresholds[pp]
        
        self.is_master = True if self.level == 10 else False
                

class AvailableSkill(models.Model):
    char_ID = models.ForeignKey(
        Character,
        on_delete=models.CASCADE
    )
    skill_ID = models.ForeignKey(
        Skill,
        on_delete=models.CASCADE
    )

    def __str__(self) -> str:
        return f"{self.skill_ID} de {self.char_ID}"

    def __repr__(self) -> str:
        return f"{self.skill_ID} ({self.char_ID})"

# Skills can be equipped in slots depending on their category
class EquippedSkill(models.Model):
    char_ID = models.OneToOneField(
        Character,
        on_delete=models.CASCADE,
        primary_key=True
    )
    intrinsic = models.ForeignKey(
        Skill,
        on_delete=models.CASCADE,
        related_name="+",
        blank=True,
        null=True
    )
    general_1 = models.ForeignKey(
        Skill,
        on_delete=models.CASCADE,
        related_name="+",
        blank=True,
        null=True
    )
    general_2 = models.ForeignKey(
        Skill,
        on_delete=models.CASCADE,
        related_name="+",
        blank=True,
        null=True
    )
    general_3 = models.ForeignKey(
        Skill,
        on_delete=models.CASCADE,
        related_name="+",
        blank=True,
        null=True
    )
    general_4 = models.ForeignKey(
        Skill,
        on_delete=models.CASCADE,
        related_name="+",
        blank=True,
        null=True
    )
    support_1 = models.ForeignKey(
        Skill,
        on_delete=models.CASCADE,
        related_name="+",
        blank=True,
        null=True
    )
    support_2 = models.ForeignKey(
        Skill,
        on_delete=models.CASCADE,
        related_name="+",
        blank=True,
        null=True
    )
    reaction = models.ForeignKey(
        Skill,
        on_delete=models.CASCADE,
        related_name="+",
        blank=True,
        null=True
    )
    movement = models.ForeignKey(
        Skill,
        on_delete=models.CASCADE,
        related_name="+",
        blank=True,
        null=True
    )
    perfect = models.ForeignKey(
        Skill,
        on_delete=models.CASCADE,
        related_name="+",
        blank=True,
        null=True
    )    

    def __str__(self) -> str:
        return f"Skills equipadas por {self.char_ID}"

    def __repr__(self) -> str:
        return f"Equipped skills ({self.char_ID})"

    def get_slots(self):
        field_names = [str(field) for field in self._meta.get_fields()]
        return (field_name[field_name.rindex('.') + 1:] for field_name in field_names[1:])
       

