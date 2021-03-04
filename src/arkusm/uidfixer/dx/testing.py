# -*- coding: utf-8 -*-
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

import arkusm.uidfixer.dx


class ArkusmUidfixerDxLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        self.loadZCML(package=arkusm.uidfixer.dx)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'arkusm.uidfixer.dx:default')


ARKUSM_UIDFIXER_DX_FIXTURE = ArkusmUidfixerDxLayer()


ARKUSM_UIDFIXER_DX_INTEGRATION_TESTING = IntegrationTesting(
    bases=(ARKUSM_UIDFIXER_DX_FIXTURE,),
    name='ArkusmUidfixerDxLayer:IntegrationTesting'
)


ARKUSM_UIDFIXER_DX_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(ARKUSM_UIDFIXER_DX_FIXTURE,),
    name='ArkusmUidfixerDxLayer:FunctionalTesting'
)


ARKUSM_UIDFIXER_DX_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        ARKUSM_UIDFIXER_DX_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE
    ),
    name='ArkusmUidfixerDxLayer:AcceptanceTesting'
)
