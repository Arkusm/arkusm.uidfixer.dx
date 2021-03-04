# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from arkusm.uidfixer.dx.testing import ARKUSM_UIDFIXER_DX_INTEGRATION_TESTING  # noqa
from plone import api

import unittest


class TestSetup(unittest.TestCase):
    """Test that arkusm.uidfixer.dx is properly installed."""

    layer = ARKUSM_UIDFIXER_DX_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if arkusm.uidfixer.dx is installed."""
        self.assertTrue(self.installer.isProductInstalled(
            'arkusm.uidfixer.dx'))

    def test_browserlayer(self):
        """Test that IArkusmUidfixerDxLayer is registered."""
        from arkusm.uidfixer.dx.interfaces import (
            IArkusmUidfixerDxLayer)
        from plone.browserlayer import utils
        self.assertIn(IArkusmUidfixerDxLayer, utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = ARKUSM_UIDFIXER_DX_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')
        self.installer.uninstallProducts(['arkusm.uidfixer.dx'])

    def test_product_uninstalled(self):
        """Test if arkusm.uidfixer.dx is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled(
            'arkusm.uidfixer.dx'))

    def test_browserlayer_removed(self):
        """Test that IArkusmUidfixerDxLayer is removed."""
        from arkusm.uidfixer.dx.interfaces import IArkusmUidfixerDxLayer
        from plone.browserlayer import utils
        self.assertNotIn(IArkusmUidfixerDxLayer, utils.registered_layers())
