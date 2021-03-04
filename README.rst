.. This README is meant for consumption by humans and pypi. Pypi can render rst files so please do not use Sphinx features.
   If you want to learn more about writing documentation, please check out: http://docs.plone.org/about/documentation_styleguide.html
   This text does not appear on pypi or github. It is a comment.

==============================================================================
arkusm.uidfixer.dx
==============================================================================

This product is based on pareto.uidfixer_. It has been adapted to work with dexterity content types. Use it to find relative links in a Plone site and replace them with 'resolveuid' ones. This product finds all links that point to items within the site, or links that contain 'resolveuid' as part of the URL, then uses traversal and the redirection tool (portal_redirection) to get to the object linked to. If that fails, the link is kept in-tact and is reported, if an object is found, the link is converted to a proper 'resolveuid' one and saved.

Prerequisites
-------------

- Plone 4 (you can use minimalplone4mrbob_ for testing)
- dexterity based content-types (plone.app.contenttypes)


Features
--------

- Find relative links in a dexterity based Plone site and replace them with 'resolveuid' ones.
- Also repairs absolute paths starting with ``http://WWW.MY-DOMAIN.ORG`` or paths starting with ``/`` (more information in browser/uidfixer.py).


Documentation
-------------

Full documentation for end users can be found in the "docs" folder.


Installation
------------

The product has not yet been released (and may never be released). Install arkusm.uidfixer.dx as development package by adding it to your buildout::

	[buildout]

	...
	extensions = mr.developer

	eggs =
		arkusm.uidfixer.dx

	auto-checkout =
		arkusm.uidfixer.dx

	test-eggs =
		arkusm.uidfixer.dx [test]


	[sources]
	arkusm.uidfixer.dx = git git@github.com:Arkusm/arkusm.uidfixer.dx

and then running ``bin/buildout``

or

add the following files to your own package

- tools.py
- browser/uidfixer-results.pt
- browser/uidfixer.pt
- browser/uidfixer.py

and add the following entry to you browser/configure.zcml::

	<browser:page
		for="*"
		name="uidfixer"
		class=".uidfixer.UIDFixerView"
		permission="zope2.ViewManagementScreens" />


Contribute
----------

- Issue Tracker: https://github.com/Arkusm/arkusm.uidfixer.dx/issues
- Source Code: https://github.com/Arkusm/arkusm.uidfixer.dx
- Documentation: https://github.com/Arkusm/arkusm.uidfixer.dx/tree/master/docs


Support
-------

https://github.com/Arkusm/arkusm.uidfixer.dx/issues


.. _pareto.uidfixer: https://github.com/pareto/pareto.uidfixer
.. _minimalplone4mrbob: https://github.com/Arkusm/minimalplone4mrbob
