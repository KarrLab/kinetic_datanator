"""
:Author: Jonathan Karr <jonrkarr@gmail.com>
:Author: Yosef Roth <yosefdroth@gmail.com>
:Date: 2017-04-10
:Copyright: 2017, Karr Lab
:License: MIT
"""

from kinetic_datanator.util import molecule_util
import copy
import enum
import numpy
import obj_model.core
import six.moves


class ConsensusMethod(enum.Enum):
    """ Represents the method by which a consensus was chosen """
    manual = 0
    mean = 1
    median = 2
    mode = 3
    weighted_mean = 4
    weighted_median = 5
    weighted_mode = 6


class Consensus(obj_model.core.Model):
    """ Represents a consensus of one or more observed values of an attribute of a component of a model

    Attributes:
        observable (:obj:`Observable`): biological component that was estimated
        value (:obj:`float`): consensus value of the attribute of the model component
        error (:obj:`float`): uncertainty of the value of the attribute of the model component
        units (:obj:`str`): units of the value of the attribute of the model component        
        method (:obj:`ConsensusMethod`): method used to calculate the consensus value and error        
        evidence (:obj:`list` of :obj:`Evidence`): list of evidence which the consensus
            value is based on
        user (:obj:`str`): user who generated the consensus
        date (:obj:`datetime.datetime`): date and time when the consensus was generated
    """
    observable = obj_model.core.ManyToOneAttribute('Observable', related_name='consensus')
    value = obj_model.core.FloatAttribute()
    error = obj_model.core.FloatAttribute()
    units = obj_model.core.StringAttribute()
    method = obj_model.core.EnumAttribute(ConsensusMethod)
    evidence = obj_model.core.ManyToManyAttribute('Evidence', related_name='consensus')
    user = obj_model.core.StringAttribute()
    date = obj_model.core.DateTimeAttribute()


class Evidence(obj_model.core.Model):
    """ Represents the observed values and their relevance which support a consensus

    Attributes:
        value (:obj:`ObservedValue`): observed value
        relevance (:obj:`float`): numeric score which indicates the relevance of the observed value to the 
            consensus
    """
    value = obj_model.core.ManyToOneAttribute('ObservedValue', related_name='evidence')
    relevance = obj_model.core.FloatAttribute()


class Observation(obj_model.core.Model):
    """ Represents an observation (one or more observed values) about a biological system

    Attributes:
        genetics (:obj:`Genetics`): the taxon, and any genetic variation from the wildtype taxon, that the component was observed in
        environment (:obj:`Environment`): environment that the component was observed in
        values (:obj:`list` of :obj:`ObservedValue`): observed values
        reference (:obj:`Reference`): reference to the reference
    """
    genetics = obj_model.core.ManyToOneAttribute('Genetics', related_name='observations')
    environment = obj_model.core.ManyToOneAttribute('Environment', related_name='observations')
    reference = obj_model.core.ManyToOneAttribute('Reference', related_name='observations')


class ObservedValue(obj_model.core.Model):
    """ Represents an observed value of a biological system

    Attributes:
        observation (:obj:`Observaton`): the collection of covariate observed values        
        value (:obj:`float`): observed value
        error (:obj:`float`): uncertainty of the observed value
        units (:obj:`units`): SI units of the observed value
        method (:obj:`str`): method that was used to make the observation
    """
    observation = obj_model.core.ManyToOneAttribute('Observation', related_name='values')
    observable = obj_model.core.ManyToOneAttribute('Observable', related_name='observed_values')
    value = obj_model.core.FloatAttribute()
    error = obj_model.core.FloatAttribute()
    units = obj_model.core.StringAttribute()
    method = obj_model.core.ManyToOneAttribute('Method', related_name='observations')


class Observable(obj_model.core.Model):
    """ Represents an observable of a biological system

    Attributes:
        interaction (:obj:`Interaction`): observed interaction
        specie (:obj:`Specie`): observed species
        compartment (:obj:`Compartment`): compartment that the spcies/interaction was observed in
        property (:obj:`str`): property that was observed
    """
    interaction = obj_model.core.ManyToOneAttribute('Interaction', related_name='observed_values')
    specie = obj_model.core.ManyToOneAttribute('Specie', related_name='observed_values')
    compartment = obj_model.core.ManyToOneAttribute('Compartment', related_name='observed_values')
    property = obj_model.core.StringAttribute()


class EntityInteractionOrProperty(obj_model.core.Model):
    """ Represents an observable of a biological system

    Attributes:
        id (:obj:`str`): identifier
        name (:obj:`str`): name
        cross_references (:obj:`list` of :obj:`Resource`): list of cross references to external resources
    """
    id = obj_model.core.StringAttribute()
    name = obj_model.core.StringAttribute()
    cross_references = obj_model.core.ManyToManyAttribute('Resource', related_name='observables')


class Compartment(EntityInteractionOrProperty):
    """ Representes a compartment in a biological system """
    pass


class Specie(EntityInteractionOrProperty):
    """ Represents a molecular species in a biological system

    Attributes:
        structure (:obj:`str`): structure
    """
    structure = obj_model.core.LongStringAttribute()

    def to_inchi(self, only_formula_and_connectivity=False):
        """ Get the structure in InChi format

        Args:
            only_formula_and_connectivity (:obj:`bool`): if :obj:`True`, return only the
                formula and connectivity layers         

        Returns:
            :obj:`str`: structure in InChi format or just the formula and connectivity layers
                if :obj:`only_formula_and_connectivity` is :obj:`True`
        """
        inchi = molecule_util.Molecule(structure=self.structure).to_inchi()
        if only_formula_and_connectivity:
            return molecule_util.InchiMolecule(inchi).get_formula_and_connectivity()
        else:
            return inchi

    def to_mol(self):
        """ Get the structure in .mol format

        Returns:
            :obj:`str`: structure in .mol format
        """
        return molecule_util.Molecule(structure=self.structure).to_mol()

    def to_openbabel(self):
        """ Get the structure as a Open Babel molecule

        Returns:
            :obj:`openbabel.OBMol`: structure as a Open Babel molecule
        """
        return molecule_util.Molecule(structure=self.structure).to_openbabel()

    def to_pybel(self):
        """ Get the structure as a Pybel molecule

        Returns:
            :obj:`pybel.Molecule`: structure as a Pybel molecule
        """
        return molecule_util.Molecule(structure=self.structure).to_pybel()

    def to_smiles(self):
        """ Get the structure in canonical SMILES format

        Returns:
            :obj:`str`: structure in canonical SMILES format
        """
        return molecule_util.Molecule(structure=self.structure).to_smiles()

    def get_similarity(self, other, fingerprint_type='fp2'):
        """ Calculate the similarity with another species

        Args:
            other (:obj:`Specie`): a second species
            fingerprint_type (:obj:`str`, optional): fingerprint type to use to calculate similarity

        Returns:
            :obj:`float`: the similarity with the other molecule
        """
        self_mol = molecule_util.Molecule(structure=self.structure)
        other_mol = molecule_util.Molecule(structure=other.structure)
        return self_mol.get_similarity(other_mol, fingerprint_type=fingerprint_type)


class PolymerSpecie(Specie):
    """ Represents a polymer

    Attributes:
        sequence (:obj:`str`): sequence
    """
    sequence = obj_model.core.LongStringAttribute()


class DnaSpecie(PolymerSpecie):
    """ Represents a DNA polymer """
    pass


class RnaSpecie(PolymerSpecie):
    """ Represents a RNA polymer """
    pass


class ProteinSpecie(PolymerSpecie):
    """ Represents a protein polymer """
    pass


class Interaction(EntityInteractionOrProperty):
    """ Represents an interaction """
    pass


class Reaction(Interaction):
    """ Represents a reaction

    Attributes:
        participants (:obj:`list` of :obj:`ReactionParticipant`): list of participants
        reversible (:obj:`bool`): :obj:`True` if the reaction is reversible
    """
    participants = obj_model.core.ManyToManyAttribute('ReactionParticipant', related_name='reactions')
    reversible = obj_model.core.BooleanAttribute()

    def get_reactants(self):
        """ Get the reactants

        Returns:
            :obj:`list` of :obj:`ReactionParticipant`: list of reactants
        """
        return list(filter(lambda p: p.coefficient < 0, self.participants))

    def get_products(self):
        """ Get the products

        Returns:
            :obj:`list` of :obj:`ReactionParticipant`: list of products
        """
        return list(filter(lambda p: p.coefficient > 0, self.participants))

    def get_modifiers(self):
        """ Get the modifiers

        Returns:
            :obj:`list` of :obj:`ReactionParticipant`: list of modifiers
        """
        return list(filter(lambda p: p.coefficient == 0, self.participants))

    def get_ordered_participants(self, collapse_repeated=True):
        """ Get an ordered list of the participants 

        Args:
            collapse_repeated (:obj:`bool`): if :obj:`True`, collapse any repeated participants

        Returns:
            :obj:`list` of :obj:`ReactionParticipant`: ordered list of reaction participants
        """

        # create copy of participants
        participants = copy.copy(list(self.participants))

        # collapse repeated participants
        if collapse_repeated:
            i_part = 0
            while i_part < len(participants):
                part = participants[i_part]
                if part.coefficient == 0:
                    participants.pop(i_part)
                    continue

                i_other_part = i_part + 1
                while i_other_part < len(participants):
                    other_part = participants[i_other_part]
                    if other_part.specie.structure == part.specie.structure and \
                            other_part.specie.id == part.specie.id and \
                            ((other_part.compartment is None and part.compartment is None) or
                                other_part.compartment.id == part.compartment.id) and \
                            numpy.sign(other_part.coefficient) == numpy.sign(part.coefficient):
                        part.coefficient += other_part.coefficient
                        participants.pop(i_other_part)
                    else:
                        i_other_part += 1

                i_part += 1

        # order participants
        participants.sort(key=lambda part: part.order if part.order is not None else 1e10)

        # return
        return participants

    def get_reactant_product_pairs(self):
        """ Get list of pairs of similar reactants and products

        Note: This requires the modeler to have ordered the reactans and products by their similarity. The modeler is required to 
        specify this pairing because it cannot easily be computed. In particular, we have tried to use Tanitomo similarity to
        predict reactant-product pairings, but this doesn't adequately capture reaction centers.

        Returns:
            :obj:`list` of :obj:`tuple` of obj:`ReactionParticipant`, :obj:`ReactionParticipant`: list of pairs of similar reactants and products
        """
        participants = self.get_ordered_participants()
        reactants = list(filter(lambda p: p.coefficient < 0, participants))
        products = list(filter(lambda p: p.coefficient > 0, participants))
        return list(six.moves.zip_longest(reactants, products))

    def get_ec_numbers(self):
        """ Get the EC numbers from the list of cross references

        Returns:
            :obj:`list` of :obj:`str`: list of EC numbers
        """
        return list(filter(lambda xr: xr.namespace == 'ec-code', self.cross_references))

    def get_manual_ec_numbers(self):
        """ Get the manually assigned EC numbers from the list of cross references

        Returns:
            :obj:`list` of :obj:`str`: list of EC manually assigned numbers
        """
        return list(filter(lambda xr: xr.namespace == 'ec-code' and xr.assignment_method ==
                           ResourceAssignmentMethod.manual, self.cross_references))

    def get_predicted_ec_numbers(self):
        """ Get the predicted EC numbers from the list of cross references

        Returns:
            :obj:`list` of :obj:`str`: list of predicted EC numbers
        """
        return list(filter(lambda xr: xr.namespace == 'ec-code' and xr.assignment_method ==
                           ResourceAssignmentMethod.predicted, self.cross_references))

    def get_ec_number(self):
        """ Get the most relevant EC number from the list of cross references

        * If the reaction has a single manually-assigned EC number, return that
        * If the reaction has multiple manually-assigned EC numbers, return an error
        * Otherwise, return the most relevant predicted EC number

        Returns:
            :obj:`str`: most relevant EC number
        """

        # return
        manual_ec_numbers = list(filter(lambda xr: xr.namespace == 'ec-code' and xr.assignment_method ==
                                        ResourceAssignmentMethod.manual, self.cross_references))
        if len(manual_ec_numbers) == 1:
            return manual_ec_numbers[0].id
        elif len(manual_ec_numbers) > 1:
            raise ValueError('Reaction {} has multiple EC numbers: {}'.format(self.id, ', '.join(xr.id for xr in manual_ec_numbers)))

        # find most relevant predicted EC number
        max_relevance = float('-inf')
        max_id = ''
        for xr in self.cross_references:
            if xr.assignment_method == ResourceAssignmentMethod.predicted and xr.relevance > max_relevance:
                max_relevance = xr.relevance
                max_id = xr.id

        return max_id


class ReactionParticipant(obj_model.core.Model):
    """ Represents a participant in a reaction

    Attributes:
        specie (:obj:`Specie`): molecular species
        compartment (:obj:`Compartment`): compartment
        coefficient (:obj:`float`): coefficient
        order (:obj:`int`): order in the list of participants
    """
    specie = obj_model.core.ManyToOneAttribute(Specie, related_name='reaction_participants')
    compartment = obj_model.core.ManyToOneAttribute(Compartment, related_name='reaction_participants')
    coefficient = obj_model.core.FloatAttribute()
    order = obj_model.core.IntegerAttribute()


class Genetics(obj_model.core.Model):
    """ Represents a taxon

    Attributes:
        taxon (obj:`str`): taxon name
        variation (:obj:`str`): the genetic variation from the wildtype taxon

        observations (:obj:`list` of :obj:`Observation`): list of observations
    """
    taxon = obj_model.core.StringAttribute()
    variation = obj_model.core.StringAttribute()

    def is_wildtype(self):
        """ Determine if the taxon is the wildtype taxon

        Returns:
            obj:`bool`: `True` if the taxon doesn't have any genetic perturbation(s)
        """
        return not self.variation

    def is_variant(self):
        """ Determine if the taxon is the wildtype stain

        Returns:
            :obj:`bool`: `True` if the taxon has at least one genetic perturbation
        """
        return not self.is_wildtype()


class Environment(obj_model.core.Model):
    """ Represents the environment (temperature, pH, media chemical composition) of an observation

    Attributes:
        temperature (:obj:`float`): temperature in Celcius
        ph (:obj:`float`): pH
        media (:obj:`str`): the chemical composition of the environment

        observations (:obj:`list` of :obj:`Observation`): list of observations
    """
    temperature = obj_model.core.FloatAttribute()
    ph = obj_model.core.FloatAttribute()
    media = obj_model.core.LongStringAttribute()


class Method(obj_model.core.Model):
    """ Represents a method used to generate an observation

    Attributes:
        name (:obj:`str`): name
        description (:obj:`str`): description

        observations (:obj:`list` of :obj:`Observation`): list of observations
    """
    name = obj_model.core.StringAttribute()
    description = obj_model.core.LongStringAttribute()


class ExperimentalMethod(Method):
    """ Represents a experimental method used to generate an observation """
    pass


class ComputationalMethod(Method):
    """ Represents a computational method used to generate an observation

    Attributes:
        version (:obj:`str`): version
        arguments (:obj:`str`): string representation of the arguments to the method
    """
    version = obj_model.core.StringAttribute()
    arguments = obj_model.core.LongStringAttribute()


class ResourceAssignmentMethod(enum.Enum):
    """ Represents the method used to assign a cross reference to an observable """
    manual = 0
    predicted = 1


class Resource(obj_model.core.Model):
    """ Represents an object in an external resource

    Attributes:
        namespace (:obj:`str`): namespace of the identifier (e.g. pubmed)
        id (:obj:`str`): identifier within :obj:`namespace` (e.g. PMID)
        relevance (:obj:`float`): numerical indicator relevance of the external resource to the observable
        assignment_method (:obj:`ResourceAssignmentMethod`): method used to assign the cross reference to the observable
    """
    namespace = obj_model.core.StringAttribute()
    id = obj_model.core.StringAttribute()
    relevance = obj_model.core.FloatAttribute()
    assignment_method = obj_model.core.EnumAttribute(ResourceAssignmentMethod)


class Reference(obj_model.core.Model):
    """ Represent a reference for an observation

    Attributes:
        title (:obj:`str`): title
        editor (:obj:`str`): editor
        author (:obj:`str`): author
        year (:obj:`int`): year
        publication (:obj:`str`): publication
        volume (:obj:`str`): volume
        number (:obj:`str`): number
        chapter (:obj:`str`): chapter
        pages (:obj:`str`): pages
        uri (:obj:`str`): uri

        observations (:obj:`list` of :obj:`Observation`): list of observations
    """
    title = obj_model.core.StringAttribute()
    editor = obj_model.core.StringAttribute()
    author = obj_model.core.StringAttribute()
    year = obj_model.core.IntegerAttribute()
    publication = obj_model.core.StringAttribute()
    volume = obj_model.core.StringAttribute()
    number = obj_model.core.StringAttribute()
    chapter = obj_model.core.StringAttribute()
    pages = obj_model.core.StringAttribute()
    uri = obj_model.core.StringAttribute()