import re
import urllib
from urlparse import urlparse

from plone.dexterity.content import DexterityContent
from plone.app.textfield.value import RichTextValue
from plone.behavior.interfaces import IBehaviorAssignable
from plone.dexterity.interfaces import IDexterityFTI

from plone.portlets.interfaces import (
    IPortletManager, IPortletAssignmentMapping, IPortletRetriever,
    ILocalPortletAssignable)
from zope.component import getUtility, getMultiAdapter, ComponentLookupError

from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.app.redirector.interfaces import IRedirectionStorage


# XXX meh, no clue what lib has this anymore... replace once remembered!
def entitize(s):
    s = s.replace('&', '&amp;')
    s = s.replace('"', '&quot;')
    s = s.replace('<', '&lt;')
    s = s.replace('>', '&gt;')
    return s


def get_all_dexterity_and_behavior_fieldnames(entry):
    if hasattr(entry, 'getObject'):
        obj = entry.getObject()
    else:
        obj = entry
    # dexterity schema
    schema = getUtility(
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


class UIDFixerView(BrowserView):
    template = ViewPageTemplateFile('uidfixer.pt')
    results_template = ViewPageTemplateFile('uidfixer-results.pt')

    def __call__(self):
        if not self.request.get('submit'):
            return self.template()
        return self.results_template()

    def results(self):
        """ return a nicely formatted list of objects for a template """
        portal_catalog = self.context.portal_catalog
        return [{
            'object': context,
            'field': field,
            'href': href,
            'resolved': not not uid,
            'resolved_url':
                (portal_catalog(UID=uid) and
                    portal_catalog(UID=uid)[0].getObject().absolute_url()),
        } for context, field, href, uid in self.fix(self.context)]

    def fix(self, context, processed_portlets=None):
        if not context.getId().startswith('portal_'):
            if processed_portlets is None:
                processed_portlets = []
            if isinstance(context, DexterityContent):
                for info in self.process_content(context):
                    yield info
            if self.request.get('fix_portlets'):
                # process portlets, both Plone ones and those from Collage
                for info in self.process_portlets(context, processed_portlets):
                    yield info
            # Recurse the children
            for item in context.objectValues():
                for info in self.fix(item, processed_portlets):
                    yield info

    def process_portlets(self, context, processed_portlets):
        for manager_name in (
                'plone.leftcolumn', 'plone.rightcolumn',
                'collage.portletmanager'):
            try:
                manager = getUtility(IPortletManager, manager_name, context)
            except ComponentLookupError:
                continue
            if manager:
                retriever = getMultiAdapter(
                    (context, manager), IPortletRetriever)
                for portlet in retriever.getPortlets():
                    assignment = portlet['assignment']
                    if assignment in processed_portlets:
                        continue
                    processed_portlets.append(assignment)
                    if hasattr(assignment, 'text'):
                        html = assignment.text
                        fixed = False
                        for href, uid, rest in self.find_uids(html, context):
                            if uid:
                                html = html.replace(
                                    'href="%s%s"' % (href, rest),
                                    'href="resolveuid/%s%s"' % (uid, rest))
                                html = html.replace(
                                    'src="%s%s"' % (href, rest),
                                    'src="resolveuid/%s%s"' % (uid, rest))
                                fixed = True
                            yield (context, portlet, href, uid)
                        if fixed and not self.request.get('dry'):
                            assignment.text = html
                            assignment._p_changed = True

    def process_content(self, context):
        fieldnames = get_all_dexterity_and_behavior_fieldnames(
                                                                    context)
        for fieldname in fieldnames:
            if hasattr(context, fieldname):
                field = getattr(context, fieldname)
                if not isinstance(field, RichTextValue):
                    continue
                html = field.raw

                fixed = False
                for href, uid, rest in self.find_uids(html, context):
                    if not uid:
                        # html = html.replace(href, 'UNRESOLVED:/%s' % (uid,))
                        continue
                    else:
                        html = html.replace(
                            'href="%s%s"' % (href, rest),
                            'href="resolveuid/%s%s"' % (uid, rest))
                        html = html.replace(
                            'src="%s%s"' % (href, rest),
                            'src="resolveuid/%s%s"' % (uid, rest))
                    fixed = True
                    yield (context, fieldname, href, uid)
                if fixed and not self.request.get('dry'):
                    setattr(context, 'text', RichTextValue(
                            html, 'text/html', 'text/x-html-safe'))

    def convert_link(self, href, context):
        if '/resolveuid/' in href and self.request.get('fix_resolveuid'):
            # IE absolute links
            _, uid = href.split('/resolveuid/')
            return uid
        elif 'resolveUid/' in href and self.request.get('fix_resolveuid'):
            # FCK Editor ./ and capitalised U links
            _, uid = href.split('resolveUid/')
            return uid
        elif self.request.get('fix_relative'):
            try:
                context = self.resolve_redirector(href, context)
            except (KeyError, AttributeError):
                pass
            else:
                try:
                    return context.UID()
                except AttributeError:
                    pass

    def resolve_redirector(self, href, context):
        redirector = getUtility(IRedirectionStorage)

        skip_links = self.request.get('skip_links', '').splitlines()

        if skip_links and any([link in href for link in skip_links if link]):
            raise KeyError

        if href.endswith('/'):
            href = href[:-1]
        chunks = [urllib.unquote(chunk) for chunk in href.split('/')]
        while chunks:
            chunk = chunks[0]
            if chunk in ('', '.'):
                chunks.pop(0)
                continue
            elif chunk == '..':
                chunks.pop(0)
                context = context.aq_parent
            else:
                break
        path = list(context.getPhysicalPath()) + chunks
        redirect = redirector.get('/'.join(path))
        if redirect is not None:
            redirected = context.restrictedTraverse(
                redirect.split('/'))
            if redirected is not None:
                context = redirected
            else:
                while chunks:
                    chunk = chunks.pop(0)
                    context = getattr(context, chunk)
        else:
            while chunks:
                chunk = chunks.pop(0)
                context = getattr(context, chunk)
        return context

    _reg_href = re.compile(r'href="([^"]+)"')
    _reg_src = re.compile(r'src="([^"]+)"')

    def find_uids(self, html, context):
        while True:
            match = self._reg_href.search(html)
            if not match:
                break
            href = match.group(1)
            # leave any views, GET vars and hashes alone
            # not entirely correct, but this seems
            # relatively solid
            rest = ''
            for s in ('@@', '?', '#', '++'):
                if s in href:
                    rest += href[href.find(s):]
                    href = href[:href.find(s)]
            html = html.replace(match.group(0), '')
            scheme, netloc, path, params, query, fragment = urlparse(href)
            # import pdb; pdb.set_trace()
            if (href and not scheme and not netloc and
                    not href.lower().startswith('resolveuid/')):
                # relative link, convert to resolveuid one
                uid = self.convert_link(href, context)
                yield href, uid, rest
        # Rince and repeat for images
        while True:
            match = self._reg_src.search(html)
            if not match:
                break
            src = match.group(1)
            # leave any views, GET vars and hashes alone
            # not entirely correct, but this seems
            # relatively solid
            rest = ''
            for s in ('@@', '?', '#', '++', '/image_'):
                if s in src:
                    rest += src[src.find(s):]
                    src = src[:src.find(s)]
            html = html.replace(match.group(0), '')
            scheme, netloc, path, params, query, fragment = urlparse(src)
            if (src and not scheme and not netloc and
                    not src.lower().startswith('resolveuid/')):
                # relative link, convert to resolveuid one
                uid = self.convert_link(src, context)
                yield src, uid, rest
