from django.db import models

class Schools(models.Model):
    school_ID = models.CharField(
        verbose_name="School ID",
        db_column="SchoolID",
        max_length=3,
        null=False,
        blank=False,
        primary_key=True
        )
    school_name = models.CharField(
        verbose_name="School Name",
        db_column="SchoolName",
        max_length=50,
        null=False,
        blank=False
        )

    def __str__(self) -> str:
        return self.school_name

    def __repr__(self) -> str:
        return f"[{self.school_ID}]: {self.school_name}"

