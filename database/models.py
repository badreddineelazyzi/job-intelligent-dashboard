from sqlalchemy import Column, Integer, String, Text, Date, Float, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Table d'association pour la relation Many-to-Many entre Jobs et Skills
job_skills = Table('job_skills', Base.metadata,
    Column('job_id', Integer, ForeignKey('fact_jobs.job_id'), primary_key=True),
    Column('skill_id', Integer, ForeignKey('dim_skills.skill_id'), primary_key=True)
)

class DimCompany(Base):
    __tablename__ = 'dim_company'
    company_id = Column(Integer, primary_key=True)
    company_name = Column(String(255), unique=True)

class DimLocation(Base):
    __tablename__ = 'dim_location'
    location_id = Column(Integer, primary_key=True)
    city = Column(String(255))
    country = Column(String(255))

class DimTime(Base):
    __tablename__ = 'dim_time'
    date_id = Column(Integer, primary_key=True)
    date = Column(Date, unique=True)
    day = Column(Integer)
    month = Column(Integer)
    year = Column(Integer)

class DimCategory(Base):
    __tablename__ = 'dim_category'
    category_id = Column(Integer, primary_key=True)
    category_name = Column(String(255), unique=True)

class DimSkills(Base):
    __tablename__ = 'dim_skills'
    skill_id = Column(Integer, primary_key=True)
    skill_name = Column(String(255), unique=True)

class FactJobs(Base):
    __tablename__ = 'fact_jobs'
    job_id = Column(Integer, primary_key=True)
    title = Column(String(255))
    description = Column(Text)
    salary_min = Column(Float)
    salary_max = Column(Float)
    source = Column(String(100))
    url = Column(Text, unique=True)

    # Clés étrangères
    company_id = Column(Integer, ForeignKey('dim_company.company_id'))
    location_id = Column(Integer, ForeignKey('dim_location.location_id'))
    category_id = Column(Integer, ForeignKey('dim_category.category_id'))
    date_id = Column(Integer, ForeignKey('dim_time.date_id'))

    # Relations Many-to-Many
    skills = relationship('DimSkills', secondary=job_skills, backref='jobs')