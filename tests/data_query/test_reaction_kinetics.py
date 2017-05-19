# -*- coding: utf-8 -*-

""" Tests of sabio_rk

:Author: Jonathan Karr <jonrkarr@gmail.com>
:Date: 2017-04-26
:Copyright: 2017, Karr Lab
:License: MIT
"""

from kinetic_datanator.core import data_model
from kinetic_datanator.data_source import sabio_rk
from kinetic_datanator.data_query import reaction_kinetics
from kinetic_datanator.util import molecule_util
import unittest


class TestReactionKineticsQuery(unittest.TestCase):

    def setUp(self):
        self.reaction_1_1_1_55 = data_model.Reaction(
            participants=[
                data_model.ReactionParticipant(
                    specie=data_model.Specie(
                        id='Lactaldehyde',
                        structure='InChI=1S/C3H6O2/c1-3(5)2-4/h2-3,5H,1H3'),
                    coefficient=-1),
                data_model.ReactionParticipant(
                    specie=data_model.Specie(
                        id='NADPH',
                        structure=(
                            'InChI=1S/C21H30N7O17P3'
                            '/c22-17-12-19(25-7-24-17)28(8-26-12)21-16(44-46(33,34)35)14(30)11(43-21)6-41-48(38,39)45-47(36,37)'
                            '40-5-10-13(29)15(31)20(42-10)27-3-1-2-9(4-27)18(23)32'
                            '/h1,3-4,7-8,10-11,13-16,20-21,29-31H,2,5-6H2,(H2,23,32)(H,36,37)(H,38,39)(H2,22,24,25)(H2,33,34,35)'
                            '/t10-,11-,13-,14-,15-,16-,20-,21-/m1/s1')),
                    coefficient=-1),
                data_model.ReactionParticipant(
                    specie=data_model.Specie(
                        id='H+',
                        structure='InChI=1S/p+1'),
                    coefficient=-1),
                data_model.ReactionParticipant(
                    specie=data_model.Specie(
                        id='1,2-Propanediol',
                        structure='InChI=1S/C3H8O2/c1-3(5)2-4/h3-5H,2H2,1H3'),
                    coefficient=1),
                data_model.ReactionParticipant(
                    specie=data_model.Specie(
                        id='NADP+',
                        structure=(
                            'InChI=1S/C21H28N7O17P3'
                            '/c22-17-12-19(25-7-24-17)28(8-26-12)21-16(44-46(33,34)35)14(30)11(43-21)6-41-48(38,39)'
                            '45-47(36,37)40-5-10-13(29)15(31)20(42-10)27-3-1-2-9(4-27)18(23)32'
                            '/h1-4,7-8,10-11,13-16,20-21,29-31H,5-6H2,(H7-,22,23,24,25,32,33,34,35,36,37,38,39)'
                            '/t10-,11-,13-,14-,15-,16-,20-,21-/m1/s1')),
                    coefficient=1),
            ])

        self.reaction_not_1_1_1_52 = data_model.Reaction(
            participants=[
                data_model.ReactionParticipant(
                    specie=data_model.Specie(
                        id='Lactaldehyde',
                        structure='InChI=1S/C3H6O2xxxxxx/c1-3(5)2-4/h2-3,5H,1H3'),
                    coefficient=-1),
                data_model.ReactionParticipant(
                    specie=data_model.Specie(
                        id='NADPH',
                        structure=(
                            'InChI=1S/C21H30N7O17P3'
                            '/c22-17-12-19(25-7-24-17)28(8-26-12)21-16(44-46(33,34)35)14(30)11(43-21)6-41-48(38,39)45-47(36,37)'
                            '40-5-10-13(29)15(31)20(42-10)27-3-1-2-9(4-27)18(23)32'
                            '/h1,3-4,7-8,10-11,13-16,20-21,29-31H,2,5-6H2,(H2,23,32)(H,36,37)(H,38,39)(H2,22,24,25)(H2,33,34,35)'
                            '/t10-,11-,13-,14-,15-,16-,20-,21-/m1/s1')),
                    coefficient=-1),
                data_model.ReactionParticipant(
                    specie=data_model.Specie(
                        id='H+',
                        structure='InChI=1S/p+1'),
                    coefficient=-1),
                data_model.ReactionParticipant(
                    specie=data_model.Specie(
                        id='1,2-Propanediol',
                        structure='InChI=1S/C3H8O2/c1-3(5)2-4/h3-5H,2H2,1H3'),
                    coefficient=1),
                data_model.ReactionParticipant(
                    specie=data_model.Specie(
                        id='NADP+',
                        structure=(
                            'InChI=1S/C21H28N7O17P3'
                            '/c22-17-12-19(25-7-24-17)28(8-26-12)21-16(44-46(33,34)35)14(30)11(43-21)6-41-48(38,39)'
                            '45-47(36,37)40-5-10-13(29)15(31)20(42-10)27-3-1-2-9(4-27)18(23)32'
                            '/h1-4,7-8,10-11,13-16,20-21,29-31H,5-6H2,(H7-,22,23,24,25,32,33,34,35,36,37,38,39)'
                            '/t10-,11-,13-,14-,15-,16-,20-,21-/m1/s1')),
                    coefficient=1),
            ],
            cross_references=[
                data_model.Resource(namespace='ec-code', id='1.1.1.52', assignment_method=data_model.ResourceAssignmentMethod.manual),
            ])

    def test_get_compounds_by_structure(self):
        q = reaction_kinetics.ReactionKineticsQuery()

        inchi = 'InChI=1S/C6H13O9P/c7-3-2(1-14-16(11,12)13)15-6(10)5(9)4(3)8/h2-10H,1H2,(H2,11,12,13)/t2-,3-,4+,5-,6+/m1/s1'

        compounds = q.get_compounds_by_structure(inchi).all()
        self.assertEqual(set(c.id for c in compounds), set([24, 1323, 1357, 1404, 1405, 1493, 1517, 1522, 24709]))
        # 1517 is a match based on the InChI conversion of its SMILES representation
        # 1524 is not in the sqlite database beacuse it it reachable from any of reaction

        compounds = q.get_compounds_by_structure(inchi, only_formula_and_connectivity=False).all()
        self.assertEqual([c.id for c in compounds], [24])

        # select=sabio_rk.Compound.id
        compounds = q.get_compounds_by_structure(inchi, only_formula_and_connectivity=False, select=sabio_rk.Compound.id).all()
        self.assertEqual([c[0] for c in compounds], [24])

    def test_get_reactions_by_compound(self):
        q = reaction_kinetics.ReactionKineticsQuery()

        d_Lactaldehyde = 'InChI=1S/C3H6O2/c1-3(5)2-4/h2-3,5H,1H3/t3-/m1/s1'

        # whole structure, reactant, select id
        q_rxn = q.get_reactions_by_compound(
            d_Lactaldehyde, only_formula_and_connectivity=False,
            role='reactant', select=sabio_rk.Reaction.id) \
            .order_by(sabio_rk.Reaction.id)
        # reactions: [548, 10424], laws: [22877, 22870, 22882, 38452, 44597, 50464, 50469, 50470]
        self.assertEqual([r[0] for r in q_rxn.all()], [548])

        # whole structure, reactant, select object
        q_rxn = q.get_reactions_by_compound(
            d_Lactaldehyde, only_formula_and_connectivity=False,
            role='reactant', select=sabio_rk.Reaction) \
            .order_by(sabio_rk.Reaction.id)
        # reactions: [548, 10424], laws: [22877, 22870, 22882, 38452, 44597, 50464, 50469, 50470]
        self.assertEqual([r.id for r in q_rxn.all()], [548])

        # formula and connectivity, reactant, select object
        q_rxn = q.get_reactions_by_compound(
            molecule_util.InchiMolecule(d_Lactaldehyde).get_formula_and_connectivity(), only_formula_and_connectivity=True,
            role='reactant', select=sabio_rk.Reaction) \
            .order_by(sabio_rk.Reaction.id)
        rxn_ids = [r.id for r in q_rxn.all()]  # laws: [50464, 26317, 28508, 41400]
        self.assertIn(548, rxn_ids)
        self.assertIn(553, rxn_ids)
        self.assertIn(554, rxn_ids)
        self.assertIn(12492, rxn_ids)

        # whole structure, product, select object
        q_rxn = q.get_reactions_by_compound(
            d_Lactaldehyde, only_formula_and_connectivity=False,
            role='product', select=sabio_rk.Reaction) \
            .order_by(sabio_rk.Reaction.id)
        self.assertEqual([r.id for r in q_rxn.all()], [10424])  # reactions: [10424], laws: [44603]

    def test_get_reactions_by_participants(self):
        q = reaction_kinetics.ReactionKineticsQuery()

        participants = self.reaction_1_1_1_55.participants

        # only_formula_and_connectivity=True, include_water_hydrogen=False
        reactions = q.get_reactions_by_participants(participants) \
            .order_by(sabio_rk.Reaction.id)
        self.assertEqual([r.id for r in reactions], [554, 2227, 10434])

        # only_formula_and_connectivity=False
        reactions = q.get_reactions_by_participants(participants, only_formula_and_connectivity=False) \
            .order_by(sabio_rk.Reaction.id)
        self.assertEqual([r.id for r in reactions], [554, 2227])

        # include_water_hydrogen=True
        reactions = q.get_reactions_by_participants(participants, include_water_hydrogen=True) \
            .order_by(sabio_rk.Reaction.id)
        self.assertEqual([r.id for r in reactions], [554, 2227, 10434])

        # select=sabio_rk.Reaction.id
        reactions = q.get_reactions_by_participants(participants, select=sabio_rk.Reaction.id) \
            .order_by(sabio_rk.Reaction.id)
        self.assertEqual([r[0] for r in reactions], [554, 2227, 10434])

    def test_get_kinetic_laws_by_participants(self):
        q = reaction_kinetics.ReactionKineticsQuery()

        participants = self.reaction_1_1_1_55.participants

        # only_formula_and_connectivity=True, include_water_hydrogen=False
        laws = q.get_kinetic_laws_by_participants(participants) \
            .order_by(sabio_rk.KineticLaw.id)
        self.assertEqual([l.id for l in laws], [22871, 22874, 22876, 22880, 28503, 28508, 38455, 46425, 46426, 46427, 46428])

        # only_formula_and_connectivity=False
        laws = q.get_kinetic_laws_by_participants(participants, only_formula_and_connectivity=False) \
            .order_by(sabio_rk.KineticLaw.id)
        self.assertEqual([l.id for l in laws], [22871, 28508, 38455, 46425, 46426, 46427, 46428])

        # include_water_hydrogen=True
        laws = q.get_kinetic_laws_by_participants(participants, include_water_hydrogen=True) \
            .order_by(sabio_rk.KineticLaw.id)
        self.assertEqual([l.id for l in laws], [22871, 22874, 22876, 22880, 28503, 28508, 38455, 46425, 46426, 46427, 46428])

        # select=sabio_rk.KineticLaw.id
        laws = q.get_kinetic_laws_by_participants(participants, select=sabio_rk.KineticLaw.id) \
            .order_by(sabio_rk.KineticLaw.id)
        self.assertEqual([l[0] for l in laws], [22871, 22874, 22876, 22880, 28503, 28508, 38455, 46425, 46426, 46427, 46428])

    def test_get_kinetic_laws_by_ec_numbers(self):
        q = reaction_kinetics.ReactionKineticsQuery()

        # single EC, match_levels=4
        laws = q.get_kinetic_laws_by_ec_numbers(['1.1.1.52'], match_levels=4).all()
        ids_52 = set([16011, 16013, 16016])
        self.assertEqual(set([l.id for l in laws]), ids_52)

        laws = q.get_kinetic_laws_by_ec_numbers(['1.1.1.55'], match_levels=4).all()
        ids_55 = set([46425, 46426, 46427, 46428])
        self.assertEqual(set([l.id for l in laws]), ids_55)

        laws = q.get_kinetic_laws_by_ec_numbers(['1.1.1.59'], match_levels=4).all()
        ids_59 = set([23931, 23932])
        self.assertEqual(set([l.id for l in laws]), ids_59)

        # multiple EC, match_levels=4
        laws = q.get_kinetic_laws_by_ec_numbers(['1.1.1.52', '1.1.1.55'], match_levels=4).all()
        self.assertEqual(set([l.id for l in laws]), ids_52 | ids_55)

        laws = q.get_kinetic_laws_by_ec_numbers(['1.1.1.52', '1.1.1.59'], match_levels=4).all()
        self.assertEqual(set([l.id for l in laws]), ids_52 | ids_59)

        laws = q.get_kinetic_laws_by_ec_numbers(['1.1.1.55', '1.1.1.59'], match_levels=4).all()
        self.assertEqual(set([l.id for l in laws]), ids_55 | ids_59)

        laws = q.get_kinetic_laws_by_ec_numbers(['1.1.1.52', '1.1.1.55', '1.1.1.59'], match_levels=4).all()
        self.assertEqual(set([l.id for l in laws]), ids_52 | ids_55 | ids_59)

        # match_levels=3
        laws = q.get_kinetic_laws_by_ec_numbers(['1.1.1.52'], match_levels=3).all()
        ids = set([l.id for l in laws])
        ids_contains = ids_52 | ids_55 | ids_59
        self.assertGreater(len(ids), len(ids_contains))
        self.assertEqual(ids_contains.difference(ids), set())

        # match_levels=3, select=sabio_rk.KineticLaw.id
        laws = q.get_kinetic_laws_by_ec_numbers(['1.1.1.52'], match_levels=3, select=sabio_rk.KineticLaw.id).all()
        ids = set([l[0] for l in laws])
        ids_contains = ids_52 | ids_55 | ids_59
        self.assertGreater(len(ids), len(ids_contains))
        self.assertEqual(ids_contains.difference(ids), set())

    def test_get_kinetic_laws_by_reaction(self):
        q = reaction_kinetics.ReactionKineticsQuery()

        laws = q.get_kinetic_laws_by_reaction(self.reaction_1_1_1_55) \
            .order_by(sabio_rk.KineticLaw.id) \
            .all()
        self.assertEqual([l.id for l in laws], [22871, 22874, 22876, 22880, 28503, 28508, 38455, 46425, 46426, 46427, 46428])

        # select=sabio_rk.KineticLaw.id
        laws = q.get_kinetic_laws_by_reaction(self.reaction_1_1_1_55, select=sabio_rk.KineticLaw.id) \
            .order_by(sabio_rk.KineticLaw.id) \
            .all()
        self.assertEqual([l[0] for l in laws], [22871, 22874, 22876, 22880, 28503, 28508, 38455, 46425, 46426, 46427, 46428])

        # get by EC
        laws = q.get_kinetic_laws_by_reaction(self.reaction_not_1_1_1_52) \
            .order_by(sabio_rk.KineticLaw.id) \
            .all()
        self.assertEqual([l.id for l in laws], [16011, 16013, 16016])

    def test_get_observed_values(self):
        q = reaction_kinetics.ReactionKineticsQuery()
        vals = q.get_observed_values(self.reaction_1_1_1_55)

        table = []
        for v in vals:
            row = [v.observable.name, None, None, v.value, v.units]
            if v.observable.parent.parent:
                row[1] = v.observable.parent.parent.name
            if v.observable.parent.parent.parent:
                row[2] = v.observable.parent.parent.parent.name
            table.append(row)

        print('\n')
        print('{:<20}  {:<20}  {:<20}  {:<20}  {:<20}'.format('Parameter', 'Compound', 'Compartment', 'Value', 'Units'))
        print('{:<20}  {:<20}  {:<20}  {:<20}  {:<20}'.format('=' * 20, '=' * 20, '=' * 20, '=' * 20, '=' * 20))
        for row in table:
            print('{:<20}  {:<20}  {:<20}  {:>20}  {:<20}'.format(row[0] or '', row[1] or '', row[2] or '', row[3] or '', row[4] or ''))

        self.assertIn(['kcat_Km', 'N-Ethylmaleimide', None, 85000.0, None], table)

    @unittest.skip('implement me')
    def test_(self):
        mol = data_model.Specie(structure=inchi)

        ec_numbers = ['1.1.1.52', '1.1.1.55']
        rxn = data_model.Reaction(cross_references=[
            data_model.Resource(namespace='ec-code', id=ec_number),
        ])
