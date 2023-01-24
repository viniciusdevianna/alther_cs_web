from django.db import models
from django.utils.translation import gettext_lazy as _

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
        INTRINSIC = "ITS", _(u"Intrínseca")
        GENERAL = "GEN", _(u"Padrão")
        SUPPORT = "SUP", _(u"Suporte")
        REACTION = "REA", _(u"Reação")
        MOVEMENT = "MOV", _(u"Movimento")
        PERFECT = "PER", _(u"Perfeita")

    name = models.CharField(
        db_column="SkillName",
        max_length=100
    )
    description = models.TextField()
    cost = models.PositiveIntegerField()
    category = models.CharField(
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

    def __str__(self) -> str:
        return self.name
    
    def __repr__(self) -> str:
        return f"{self.name} ({self.path}, {self.category})"

class Character(models.Model):

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
    inventory = models.TextField()
    annotations = models.TextField()
    coin = models.CharField(
        max_length=200
    )

    def __str__(self) -> str:
        return self.name
    
    def __repr__(self) -> str:
        return f"{self.name} ({self.race}, {self.school})"
