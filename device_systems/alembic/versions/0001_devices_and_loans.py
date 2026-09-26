from alembic import op
import sqlalchemy as sa

revision = "0001_devices_loans"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER NOT NULL PRIMARY KEY,
        name VARCHAR NOT NULL,
        email VARCHAR NOT NULL UNIQUE,
        role VARCHAR NOT NULL,
        is_active BOOLEAN DEFAULT 1,
        created_at DATETIME
    )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_users_id ON users (id)")
    op.execute("CREATE UNIQUE INDEX IF NOT EXISTS ix_users_email ON users (email)")
    op.create_table(
        "devices",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("serial_number", sa.String(), nullable=False),
        sa.Column("device_type", sa.String(), nullable=False),
        sa.Column("brand", sa.String(), nullable=True),
        sa.Column("is_available", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_devices_id", "devices", ["id"])
    op.create_index("ix_devices_serial_number", "devices", ["serial_number"], unique=True)
    op.create_index("ix_devices_device_type", "devices", ["device_type"])
    op.create_index("ix_devices_brand", "devices", ["brand"])
    op.create_index("ix_devices_is_available", "devices", ["is_available"])
    op.create_table(
        "loans",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("device_id", sa.Integer(), sa.ForeignKey("devices.id"), nullable=False),
        sa.Column("loan_date", sa.DateTime(), nullable=False),
        sa.Column("return_date", sa.DateTime(), nullable=True),
        sa.Column("status", sa.String(), nullable=False),
    )
    op.create_index("ix_loans_id", "loans", ["id"])
    op.create_index("ix_loans_user_id", "loans", ["user_id"])
    op.create_index("ix_loans_device_id", "loans", ["device_id"])
    op.create_index("ix_loans_status", "loans", ["status"])

def downgrade():
    op.drop_table("loans")
    op.drop_index("ix_devices_is_available", table_name="devices")
    op.drop_index("ix_devices_brand", table_name="devices")
    op.drop_index("ix_devices_device_type", table_name="devices")
    op.drop_index("ix_devices_serial_number", table_name="devices")
    op.drop_index("ix_devices_id", table_name="devices")
    op.drop_table("devices")
