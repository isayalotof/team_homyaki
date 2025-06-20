from sqlalchemy import Column, Integer, String, Text, Table, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base_class import Base

tour_tour_type = Table(
    'tour_tour_type', Base.metadata,
    Column('tour_id', Integer, ForeignKey('tours.id'), primary_key=True),
    Column('tour_type_id', Integer, ForeignKey('tour_types.id'), primary_key=True)
)

class TourType(Base):
    __tablename__ = 'tour_types'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(Text)
    
    tours = relationship("Tour", secondary=tour_tour_type, back_populates="tour_types")