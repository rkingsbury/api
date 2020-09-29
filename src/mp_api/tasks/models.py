from datetime import datetime
from enum import Enum
from typing import List

from monty.json import MontyDecoder
from mp_api.materials.models import Structure, Composition
from pydantic import BaseModel, Field, validator

from pymatgen.core.periodic_table import Element

monty_decoder = MontyDecoder()


class TaskType(str, Enum):
    """
    The type of calculation
    """

    EMPTY = ""
    GGA_NSCF_Line = "GGA NSCF Line"
    GGA_NSCF_Uniform = "GGA NSCF Uniform"
    GGA_Static = "GGA Static"
    GGA_Structure_Optimization = "GGA Structure Optimization"
    GGA_U_NSCF_Line = "GGA+U NSCF Line"
    GGA_U_NSCF_Uniform = "GGA+U NSCF Uniform"
    GGA_U_Static = "GGA+U Static"
    GGA_U_Structure_Optimization = "GGA+U Structure Optimization"


class PotcarSpec(BaseModel):
    symbols: List[str]
    functional: str


class OrigInputs(BaseModel):
    incar: str = Field(
        None, description="Pymatgen object representing the INCAR file",
    )

    poscar: str = Field(
        None, description="Pymatgen object representing the POSCAR file",
    )

    kpoints: str = Field(
        None, description="Pymatgen object representing the KPOINTS file",
    )

    potcar: PotcarSpec = Field(
        None, description="Pymatgen object representing the POTCAR file",
    )

    # Convert all other input files into strings
    @validator("incar", "kpoints", "poscar", pre=True)
    def convert_to_string(cls, input_dict):
        obj = monty_decoder.process_decoded(input_dict)
        return str(obj)


class OutputDoc(BaseModel):
    structure: Structure = Field(
        None,
        title="Output Structure",
        description="Output Structure from the VASP calculation",
    )

    density: float = Field(..., description="Density of in units of g/cc")
    energy: float = Field(..., description="Total Energy in units of eV")
    forces: List[List[float]] = Field(
        None, description="The force on each atom in units of eV/AA"
    )
    stress: List[List[float]] = Field(
        None, description="The stress on the cell in units of kB"
    )


class InputDoc(BaseModel):
    structure: Structure = Field(
        None,
        title="Input Structure",
        description="Output Structure from the VASP calculation",
    )


class CalcsReversedDoc(BaseModel):
    output: dict = Field(
        None,
        title="Calcs Reversed Output",
        description="Detailed output data for VASP calculations in calcs reversed.",
    )


class TaskDoc(BaseModel):
    """
    Model for task document generated by ATOMATE, each task correspond to a single calculation
    """

    tags: List[str] = Field(
        None, title="tag", description="Metadata tagged to a given task"
    )

    calcs_reversed: List[CalcsReversedDoc] = Field(
        None,
        title="Calcs reversed data",
        description="Detailed data for each VASP calculation contributing to the task document.",
    )

    task_type: TaskType = Field(None, description="The type of calculation")

    task_id: str = Field(
        None,
        description="The ID of this calculation, used as a universal reference across property documents."
        "This comes in the form: mp-******",
    )

    # Structure metadata
    nsites: int = Field(None, description="Total number of sites in the structure")
    elements: List[Element] = Field(
        None, description="List of elements in the material"
    )
    nelements: int = Field(None, title="Number of Elements")
    composition: Composition = Field(
        None, description="Full composition for the material"
    )
    composition_reduced: Composition = Field(
        None,
        title="Reduced Composition",
        description="Simplified representation of the composition",
    )
    formula_pretty: str = Field(
        None,
        title="Pretty Formula",
        description="Cleaned representation of the formula",
    )
    formula_anonymous: str = Field(
        None,
        title="Anonymous Formula",
        description="Anonymized representation of the formula",
    )
    chemsys: str = Field(
        None,
        title="Chemical System",
        description="dash-delimited string of elements in the material",
    )

    orig_inputs: OrigInputs = Field(
        None,
        description="The exact set of input parameters used to generate the current task document.",
    )

    input: InputDoc = Field(
        None,
        description="The input structure used to generate the current task document.",
    )

    output: OutputDoc = Field(
        None,
        description="The exact set of output parameters used to generate the current task document.",
    )

    last_updated: datetime = Field(
        None,
        description="Timestamp for the most recent calculation for this task document",
    )

    # Make sure that the datetime field is properly formatted
    @validator("last_updated", pre=True)
    def last_updated_dict_ok(cls, v):
        return monty_decoder.process_decoded(v)