import pickle

from sqlalchemy import create_engine, Column, Integer, Binary, String, Float, exists
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.exc import MultipleResultsFound


from enviroms.encapsulation.settings.molecular_id.MolecularIDSettings import MoleculaSearchSettings

Base = declarative_base()

class MolecularFormulaTable(Base):  
    
    __tablename__ = 'molform'

    id = Column( Binary, primary_key=True)
    nominal_mz= Column(Integer, nullable=False)
    ion_type = Column(String, nullable=False)
    ion_charge = Column(Integer, nullable=False)
    classe = Column(String, nullable=False)
    
    C = Column(Integer, nullable=False)
    H = Column(Integer, nullable=True)
    N = Column(Integer, nullable=True)
    O = Column(Integer, nullable=True)
    S = Column(Integer, nullable=True)
    P = Column(Integer, nullable=True)
    DBE = Column(Float, nullable=False)

    def __init__(self, kargs): 
        
        self.id = kargs['mol_formula']
        self.nominal_mz =kargs['nominal_mass']
        self.ion_type = kargs['ion_type']
        self.ion_charge = kargs['ion_charge']
        self.classe = kargs['classe']
        self.C = kargs['C']
        self.H = kargs['H']
        self.N = kargs['N']
        self.O = kargs['O']
        self.S = kargs['S']
        self.P = kargs['P']
        self.DBE = kargs['DBE']
       
    def __repr__(self):
        return "<MolecularFormulaTable(classe='%s', nominal_mass='%i', ion_type='%s', ion_charge='%i')>" % (
                                    self.classe, self.nominal_mz, self.ion_type, self.ion_charge)

class MolForm_SQL:
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # make sure the dbconnection gets closed
        self.commit()
        self.session.close()
        self.engine.dispose()

    def __enter__(self):
        
        self.engine = create_engine('sqlite:///{DB}'.format(DB='res/molformulas.sqlite'), connect_args={'timeout': 15})
        
        Base.metadata.create_all(self.engine)

        Session = sessionmaker(bind=self.engine)
        
        self.session = Session()

        return self
    
    def add_all(self, sql_molform_list):
        
        self.session.add_all( [MolecularFormulaTable(sql_molform_dict)  for sql_molform_dict in sql_molform_list] )
    
    def add_entry(self,sql_molform): 

        one_formula = MolecularFormulaTable(sql_molform)  
        self.session.add(one_formula)  

    def commit(self):
        
        try:
            self.session.commit()  
        except SQLAlchemyError as e:
            self.session.rollback()
            print(str(e))
            
    def check_entry(self,classe):
        # this is way too slow, create a pos and neg table
        #try:
        #yes = self.session.query(MolecularFormulaTable.id).filter(MolecularFormulaTable.classe==classe).filter(MolecularFormulaTable.ion_charge == MoleculaSearchSettings.ion_charge).scalar() is not None
        
        #except MultipleResultsFound as e:
        #    yes = True
        #except MultipleResultsFound as e:
        #    yes = True
        yes = self.session.query(exists().where(
            (MolecularFormulaTable.classe == classe) &
            (MolecularFormulaTable.ion_charge == MoleculaSearchSettings.ion_charge))).scalar()

        return yes
    
    def get_entries(self,classe, ion_type, nominal_mz):
        
        mol_formulas = self.session.query(MolecularFormulaTable).filter(
            MolecularFormulaTable.nominal_mz == nominal_mz,
            MolecularFormulaTable.classe == classe, 
            MolecularFormulaTable.ion_type == ion_type,
            MolecularFormulaTable.ion_charge == MoleculaSearchSettings.ion_charge,
            MolecularFormulaTable.H/MolecularFormulaTable.C >= MoleculaSearchSettings.hc_filter,
            MolecularFormulaTable.O/MolecularFormulaTable.C >= MoleculaSearchSettings.oc_filter,
            MolecularFormulaTable.DBE <= MoleculaSearchSettings.max_dbe,
            MolecularFormulaTable.DBE <= MoleculaSearchSettings.min_dbe)
            
        
        #mol_formulas = mol_formulas.filter(ion_type = ion_type)

        #mol_formulas = mol_formulas.filter(ion_charge = MoleculaSearchSettings.ion_charge)

        return [pickle.loads(formula.id) for formula in mol_formulas]
       

    def update_entry(self, entry):
        
        entry.title = "Some2016Film"  
        self.session.commit()

    def delete_entry(self, entry):
        
        try:
            self.session.delete(entry)  
            self.session.commit()  
        
        except SQLAlchemyError as e:
            self.session.rollback()
            print(str(e))


   