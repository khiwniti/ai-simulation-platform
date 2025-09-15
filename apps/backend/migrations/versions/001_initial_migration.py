"""Initial migration with core models

Revision ID: 001
Revises: 
Create Date: 2024-12-09 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create workbooks table
    op.create_table('workbooks',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create notebooks table
    op.create_table('notebooks',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('workbook_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['workbook_id'], ['workbooks.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create cells table
    op.create_table('cells',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('notebook_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('cell_type', sa.Enum('CODE', 'MARKDOWN', 'PHYSICS', 'VISUALIZATION', name='celltype'), nullable=False),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('execution_count', sa.Integer(), nullable=True),
        sa.Column('position', sa.Integer(), nullable=False),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['notebook_id'], ['notebooks.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create cell_outputs table
    op.create_table('cell_outputs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('cell_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('output_type', sa.String(length=50), nullable=False),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('output_index', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['cell_id'], ['cells.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create simulation_contexts table
    op.create_table('simulation_contexts',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('notebook_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('physics_parameters', sa.JSON(), nullable=True),
        sa.Column('execution_state', sa.String(length=20), nullable=True),
        sa.Column('active_agents', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('gpu_device_id', sa.Integer(), nullable=True),
        sa.Column('gpu_memory_limit', sa.Float(), nullable=True),
        sa.Column('gpu_compute_capability', sa.String(length=10), nullable=True),
        sa.Column('last_execution_time', sa.Float(), nullable=True),
        sa.Column('memory_usage', sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(['notebook_id'], ['notebooks.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create gpu_resource_configs table
    op.create_table('gpu_resource_configs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('device_name', sa.String(length=255), nullable=False),
        sa.Column('device_id', sa.Integer(), nullable=False),
        sa.Column('total_memory', sa.Float(), nullable=False),
        sa.Column('compute_capability', sa.String(length=10), nullable=False),
        sa.Column('is_available', sa.String(length=10), nullable=True),
        sa.Column('current_usage', sa.Float(), nullable=True),
        sa.Column('driver_version', sa.String(length=50), nullable=True),
        sa.Column('cuda_version', sa.String(length=50), nullable=True),
        sa.Column('physx_compatible', sa.String(length=10), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create agent_interactions table
    op.create_table('agent_interactions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('agent_type', sa.String(length=20), nullable=False),
        sa.Column('query', sa.Text(), nullable=False),
        sa.Column('response', sa.Text(), nullable=False),
        sa.Column('context', sa.JSON(), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('notebook_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('cell_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('response_time', sa.Float(), nullable=True),
        sa.Column('tokens_used', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['cell_id'], ['cells.id'], ),
        sa.ForeignKeyConstraint(['notebook_id'], ['notebooks.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for better performance
    op.create_index('idx_notebooks_workbook_id', 'notebooks', ['workbook_id'])
    op.create_index('idx_cells_notebook_id', 'cells', ['notebook_id'])
    op.create_index('idx_cells_position', 'cells', ['notebook_id', 'position'])
    op.create_index('idx_cell_outputs_cell_id', 'cell_outputs', ['cell_id'])
    op.create_index('idx_simulation_contexts_notebook_id', 'simulation_contexts', ['notebook_id'])
    op.create_index('idx_agent_interactions_session_id', 'agent_interactions', ['session_id'])
    op.create_index('idx_agent_interactions_notebook_id', 'agent_interactions', ['notebook_id'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_agent_interactions_notebook_id')
    op.drop_index('idx_agent_interactions_session_id')
    op.drop_index('idx_simulation_contexts_notebook_id')
    op.drop_index('idx_cell_outputs_cell_id')
    op.drop_index('idx_cells_position')
    op.drop_index('idx_cells_notebook_id')
    op.drop_index('idx_notebooks_workbook_id')
    
    # Drop tables in reverse order
    op.drop_table('agent_interactions')
    op.drop_table('gpu_resource_configs')
    op.drop_table('simulation_contexts')
    op.drop_table('cell_outputs')
    op.drop_table('cells')
    op.drop_table('notebooks')
    op.drop_table('workbooks')
    
    # Drop enum types
    op.execute('DROP TYPE IF EXISTS celltype')