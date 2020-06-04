"""empty message

Revision ID: df9ac369a914
Revises: 
Create Date: 2020-06-03 23:50:50.770625

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'df9ac369a914'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('selected_answers',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('question_id', sa.Integer(), nullable=True),
    sa.Column('answer_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['answer_id'], ['answers.id'], ),
    sa.ForeignKeyConstraint(['question_id'], ['questions.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('selected_answers')
    # ### end Alembic commands ###
