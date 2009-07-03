# -*- coding: utf-8 -*-
from StringIO import StringIO
from genshi.builder import tag
from genshi.filters import Transformer
from trac.config import Option
from trac.core import *
from trac.mimeview.api import Mimeview, get_mimetype, Context, WikiTextRenderer
from trac.ticket import ITicketChangeListener, Ticket, ITicketManipulator
from trac.ticket.model import Ticket, Component
from trac.util import TracError
from trac.web import IRequestHandler
from trac.web.api import ITemplateStreamFilter
from trac.web.chrome import INavigationContributor, ITemplateProvider
from trac.wiki.model import WikiPage
import commands
import re
import simplejson as json
from symfonyerrors.api import *

class SymfonyErrorPlugin(Component):
    """
        Provides routing
         - delete error
         - show errors
         - create tickets from errors (cron job)
    """    
    implements(INavigationContributor, IRequestHandler, ITemplateProvider)
    
    default_owner = Option('symfonyerrors','default_ticket_owner', 'cron')

    # INavigationContributor method
    def get_active_navigation_item(self, req):
        return 'bugs'
    
    # INavigationContributor method
    def get_navigation_items(self, req):
        yield ('mainnav', 'bugs',
               tag.a('Bugs', href=req.href.bugs()))
    
    # IRequestHandler method
    def match_request(self, req):
        return re.match(r'/bugs(?:_trac)?(?:/.*)?$', req.path_info)

    # IRequestHandler method
    def process_request(self, req):
    	template_data = {}
        peer = SymfonyErrorPeer(self.env) 
    
    	if(req.args.get('cron_job')):
    		self.import_tickets()
    		return 'cron.html', template_data, None
    
        delete_bug_id = req.args.get('delete_bug_id', '')
        
        if delete_bug_id:
            peer.delete_by_hash(delete_bug_id)
            template_data.update(msg="Similar bugs deleted")
            
        sf_errors = peer.select_grouped()

    	template_data.update(sf_errors=sf_errors, cmd=commands, json=json, se=self, io=StringIO)
    
    	return 'symfony_errors.html', template_data, None

    # ITemplateProvider method
    def get_templates_dirs(self):
        from pkg_resources import resource_filename
        return [resource_filename(__name__, 'templates')]
    
    # Create tickets from symfony errors
    def import_tickets(self):
        trac_cursor = self.env.get_db_cnx().cursor()
        peer = SymfonyErrorPeer(self.env)
        
        owners = {}
        trac_cursor.execute("select owner, name from component")         
        for name, owner in trac_cursor:
            owners[name] = owner
        
        for error in peer.select_grouped():
            
            # ticket with current hash key not exists ?
            trac_cursor.execute("select ticket from ticket_custom where name = 'symfony_error_key' and value = '%s'" % error['hash_key'])            
            
            existing = trac_cursor.fetchone()
            if not existing:
                ticket = Ticket(self.env)
                ticket.values['summary'] = 'Bug #' + error['hash_key'] + ' ' + error['message']
                ticket.values['symfony_error_key'] = error['hash_key']
                ticket.values['reporter'] = 'cron'
                ticket.values['resolution'] = 'new'
                ticket.values['status'] = 'new'
                ticket.values['milestone'] = '0.3.1'
                if error['module_name'] in owners:
                    owner = owners[error['module_name']]
                else:
                    owner = self.default_owner
                    
                                       
                ticket.values['owner'] = owner 
                ticket.insert()
     
class SymfonyErrorTicketChange(Component):
    """
    Monitoring ticket status
    Delete errors when ticket is closed
    """
    implements(ITicketChangeListener)
    
    def __init__(self):
        pass    
    
    def ticket_created(self, ticket):
        pass
    
    def ticket_deleted(self, ticket):
        pass    
    
    def ticket_changed(self, ticket, comment, author, old_values):
        peer = SymfonyErrorPeer(self.env)
        if 'symfony_error_key' in ticket.values:
            if ticket.values['symfony_error_key'] != '' and ticket.values['status'] == 'closed': 
                peer.delete_by_hash(ticket.values['symfony_error_key'])
     
     
class SymfonyErrorTicketDescription(Component):
    """
    Ticket Description containing error description fetched by custom ticket field name symfony_error_key
    """        
    implements(ITemplateStreamFilter, ITemplateProvider)

    def filter_stream(self, req, method, filename, stream, data):
        if filename != 'ticket.html':
            return stream

    	values = data['ticket'].values
    	
    	if not 'symfony_error_key' in values:
    		return stream
  
    	id = values['symfony_error_key']
        
        if id == '':
            return stream
    	
    	content = "[[ShowSymfonyError(%s)]]" % id
    	content = WikiTextRenderer(self.env).render(Context.from_request(req), 'text/x-trac-wiki', content)
    	stream |= Transformer("//div[@class='description']").after(tag.div(content, **{'class': "description" }))
    
    	return stream

    def get_templates_dirs(self):
        return []

    def get_htdocs_dirs(self):
        return []
    
from trac import util
from trac.perm import IPermissionRequestor, PermissionSystem
from trac.util import Markup
from trac.ticket.admin import TicketAdminPanel


class SymfonyErrorsAdminPanel(TicketAdminPanel):
    _type = 'symfonyerrors'
    _label = ('Symfony errors', 'Symfony Errors')

    def _render_admin_panel(self, req, cat, page, component):
        req.perm.require('TICKET_ADMIN')        
        keys = ['dbhost','dbuser','dbname','dbpasswd','dbport', 'default_ticket_owner']
        
        settings = {}
        
        if req.method == 'POST':
            for key in keys:
                self.config.set(self._type, key, req.args.get(key))
            self.config.save()
        
        for key in keys:
            settings[key] = self.config.get(self._type, key)
                                    
        data = { 'settings': settings }     

        return 'webadmin.html', data