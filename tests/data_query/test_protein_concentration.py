# -*- coding: utf-8 -*-

""" Tests of common_schemy protein concentration queries

:Author: Saahith Pochiraju <saahith116@gmail.com>
:Date: 2017-09-19
:Copyright: 2017, Karr Lab
:License: MIT
"""

from kinetic_datanator.core import data_model
from kinetic_datanator.data_query import protein_concentrations
from kinetic_datanator.app import models, flask_common_schema
import tempfile
import shutil
import unittest

class TestProteinConcentrationsQueryGenerator(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.cache_dirname = tempfile.mkdtemp()
        flk = flask_common_schema.FlaskCommonSchema(cache_dirname=self.cache_dirname)

        self.protein_P00323 = flk.session.query(models.ProteinSubunit).filter_by(uniprot_id = 'P00323').first()

    @classmethod
    def tearDownClass(self):
        shutil.rmtree(self.cache_dirname)

    def test_filter_observed_values(self):
        q = protein_concentrations.ProteinConcentrationsQueryGenerator()

        vals = q.get_observed_values(self.protein_P00323)

        for items in vals:
            self.assertEqual(items.units, 'PPM')
            self.assertEqual(items.observable.specie.sequence, self.protein_P00323.canonical_sequence)
            if items.observable.specie.cross_references[0].id == '882/882-Desulfo_Form_Exp_SC_zhang_2006.txt':
                self.assertEqual(items.value, 1003.0)

    def test_get_abundance_by_uniprot(self):
        q = protein_concentrations.ProteinConcentrationsQueryGenerator()

        uniprot = self.protein_P00323.uniprot_id
        abundances = q.get_abundance_by_uniprot(uniprot).filter(
            models.AbundanceData.pax_load.in_([1, 2])).all()
        self.assertEqual(set(c.abundance for c in abundances),
                         set([1003.0, 1336.0]))

    def test_get_abundance_by_gene_name(self):
        q = protein_concentrations.ProteinConcentrationsQueryGenerator()

        gene_name = 'rplO'
        abundances = q.get_abundance_by_gene_name(gene_name).filter(
            models.AbundanceData.pax_load.in_([1, 2])).all()
        self.assertEqual(set(c.abundance for c in abundances),
                         set([1027.0, 1861.0]))

    def test_get_abundance_by_sequence(self):
        q = protein_concentrations.ProteinConcentrationsQueryGenerator()

        sequence = self.protein_P00323.canonical_sequence
        abundances = q.get_abundance_by_sequence(sequence).filter(
            models.AbundanceData.pax_load.in_([1, 2])).all()
        self.assertEqual(set(c.abundance for c in abundances),
                         set([1003.0, 1336.0]))

    def test_get_abundance_by_entrez(self):
        q = protein_concentrations.ProteinConcentrationsQueryGenerator()

        entrez_id = self.protein_P00323.entrez_id
        abundances = q.get_abundance_by_entrez(entrez_id).filter(
            models.AbundanceData.pax_load.in_([1, 2])).all()
        self.assertEqual(set(c.abundance for c in abundances),
                         set([1003.0, 1336.0]))

    def test_get_abundance_by_mass(self):
        q = protein_concentrations.ProteinConcentrationsQueryGenerator()

        mass = self.protein_P00323.mass
        abundances = q.get_abundance_by_mass(mass).filter(
            models.AbundanceData.pax_load.in_([1, 2])).all()
        self.assertEqual(set(c.abundance for c in abundances),
                         set([1003.0, 1336.0]))

    def test_get_abundance_by_length(self):
        q = protein_concentrations.ProteinConcentrationsQueryGenerator()

        length = self.protein_P00323.length
        abundances = q.get_abundance_by_length(length).filter(
            models.AbundanceData.pax_load.in_([1, 2])).all()
        self.assertEqual(set(c.abundance for c in abundances),
                         set([1003.0, 1336.0, 1027.0, 1861.0]))
