from Products.CMFCore.utils import getToolByName
from plone.behavior.interfaces import IBehaviorAssignable
from plone.dexterity.interfaces import IDexterityFTI
import zope.component

def get_relative_url(context):
    """
    Get the relative url
    @return string
    """
    portal_url = getToolByName(context, "portal_url")
    portal = portal_url.getPortalObject()
    context_path = context.getPhysicalPath()
    site_path = portal.getPhysicalPath()
    relative_path = context_path[len(site_path):]
    return '{}'.format("/".join(relative_path))

def get_all_dexterity_and_behavior_fieldnames(entry):
    """
    Schema and behavior introspection
    @return list of field names
    """
    if hasattr(entry, 'getObject'):
        obj = entry.getObject()
    else:
        obj = entry
    # dexterity schema
    schema = zope.component.getUtility(
        IDexterityFTI, name=obj.portal_type).lookupSchema()
    fields = [schema[name] for name in schema]
    # behaviors
    assignable = IBehaviorAssignable(obj)
    for behavior in assignable.enumerateBehaviors():
        behavior_schema = behavior.interface
        for name in behavior_schema:
            fields.append(behavior_schema[name])
    # field names
    fieldnames = [entry.__name__ for entry in fields]
    return fieldnames

def decode_utf8(value):
    """
    Decode value, if not unicode
    @return: unicode string
    """
    if not isinstance(value, unicode):
        if value:
            value = value.decode('utf-8')
        else:
            value = u''
    return value
