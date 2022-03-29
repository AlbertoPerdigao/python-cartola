"""Initial migration.

Revision ID: e277d5a6559c
Revises: 
Create Date: 2022-03-23 14:41:39.721344

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "e277d5a6559c"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "months",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("tax", sa.Numeric(precision=7, scale=2), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "teams",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("slug", sa.String(length=128), nullable=False),
        sa.Column("id_tag", sa.String(length=128), nullable=False),
        sa.Column("url_escudo_png", sa.String(length=255), nullable=False),
        sa.Column("player_name", sa.String(length=128), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "payments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("amount", sa.Numeric(precision=7, scale=2), nullable=False),
        sa.Column("teams_id", sa.Integer(), nullable=False),
        sa.Column("months_id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["months_id"],
            ["months.id"],
        ),
        sa.ForeignKeyConstraint(
            ["teams_id"],
            ["teams.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "rounds",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("round_number", sa.Integer(), nullable=False),
        sa.Column("awarded", sa.Boolean(), nullable=False),
        sa.Column("months_id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["months_id"],
            ["months.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "prizes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column(
            "total_prize_percentage", sa.Numeric(precision=7, scale=2), nullable=False
        ),
        sa.Column(
            "first_place_percentage", sa.Numeric(precision=7, scale=2), nullable=False
        ),
        sa.Column(
            "second_place_percentage", sa.Numeric(precision=7, scale=2), nullable=False
        ),
        sa.Column(
            "tird_place_percentage", sa.Numeric(precision=7, scale=2), nullable=False
        ),
        sa.Column(
            "fourth_place_percentage", sa.Numeric(precision=7, scale=2), nullable=False
        ),
        sa.Column("months_id", sa.Integer(), nullable=False),
        sa.Column("rounds_id", sa.Integer(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["months_id"],
            ["months.id"],
        ),
        sa.ForeignKeyConstraint(
            ["rounds_id"],
            ["rounds.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "scores",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("value", sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column("cartoletas", sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column("teams_id", sa.Integer(), nullable=False),
        sa.Column("rounds_id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["rounds_id"],
            ["rounds.id"],
        ),
        sa.ForeignKeyConstraint(
            ["teams_id"],
            ["teams.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "winners",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("place", sa.Integer(), nullable=False),
        sa.Column("prize_value", sa.Numeric(precision=7, scale=2), nullable=False),
        sa.Column("teams_id", sa.Integer(), nullable=False),
        sa.Column("prizes_id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["prizes_id"],
            ["prizes.id"],
        ),
        sa.ForeignKeyConstraint(
            ["teams_id"],
            ["teams.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("winners")
    op.drop_table("scores")
    op.drop_table("prizes")
    op.drop_table("rounds")
    op.drop_table("payments")
    op.drop_table("teams")
    op.drop_table("months")
    # ### end Alembic commands ###
