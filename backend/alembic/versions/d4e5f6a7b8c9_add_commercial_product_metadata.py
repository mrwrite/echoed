"""add commercial product metadata

Revision ID: d4e5f6a7b8c9
Revises: b3d2c1e4f607
Create Date: 2026-06-30 18:05:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "d4e5f6a7b8c9"
down_revision: Union[str, Sequence[str], None] = "b3d2c1e4f607"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("products", sa.Column("subtitle", sa.String(), nullable=True))
    op.add_column("products", sa.Column("slug", sa.String(), nullable=True))
    op.add_column("products", sa.Column("hero_image_url", sa.String(), nullable=True))
    op.add_column("products", sa.Column("thumbnail_url", sa.String(), nullable=True))
    op.add_column("products", sa.Column("visibility", sa.String(), nullable=False, server_default="draft"))
    op.add_column("products", sa.Column("pricing_model", sa.String(), nullable=False, server_default="internal"))
    op.add_column("products", sa.Column("price_placeholder", sa.String(), nullable=True))
    op.add_column("products", sa.Column("currency", sa.String(), nullable=True))
    op.add_column("products", sa.Column("audience", sa.String(), nullable=True))
    op.add_column("products", sa.Column("difficulty", sa.String(), nullable=True))
    op.add_column("products", sa.Column("estimated_duration", sa.String(), nullable=True))
    op.add_column("products", sa.Column("tags", sa.JSON(), nullable=True))
    op.add_column("products", sa.Column("category", sa.String(), nullable=True))
    op.add_column("products", sa.Column("version", sa.String(), nullable=True))
    op.add_column("products", sa.Column("language", sa.String(), nullable=True))
    op.add_column("products", sa.Column("last_updated", sa.DateTime(), nullable=True))
    op.add_column("products", sa.Column("certificate_available", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("products", sa.Column("featured", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.create_index(op.f("ix_products_slug"), "products", ["slug"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_products_slug"), table_name="products")
    op.drop_column("products", "featured")
    op.drop_column("products", "certificate_available")
    op.drop_column("products", "last_updated")
    op.drop_column("products", "language")
    op.drop_column("products", "version")
    op.drop_column("products", "category")
    op.drop_column("products", "tags")
    op.drop_column("products", "estimated_duration")
    op.drop_column("products", "difficulty")
    op.drop_column("products", "audience")
    op.drop_column("products", "currency")
    op.drop_column("products", "price_placeholder")
    op.drop_column("products", "pricing_model")
    op.drop_column("products", "visibility")
    op.drop_column("products", "thumbnail_url")
    op.drop_column("products", "hero_image_url")
    op.drop_column("products", "slug")
    op.drop_column("products", "subtitle")
