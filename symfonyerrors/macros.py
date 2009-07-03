from trac.core import *
from trac.wiki.api import parse_args, IWikiMacroProvider
from trac.wiki.macros import WikiMacroBase
from trac.util.html import html
from trac.util.text import to_unicode
from symfonyerrors.api import *

class SymfonyErrorMacro(WikiMacroBase):
    """
    Macro displaying error description for given error hash key
    """      
    implements(IWikiMacroProvider)
          
    def get_macros(self):
        return ['ShowSymfonyError']  
    
    def expand_macro(self, formatter, name, content):
        arguments = content.split(',')
        error_hash = arguments[0]
        
        peer = SymfonyErrorPeer(self.env)
        msg = peer.retrieve_by_hash(error_hash)
        if msg:
            html_msg_h3 = html.h3('Komunikat')            
            html_msg = html.p(html.b(msg[0]))
            html_uri_h3 = html.h3('Adres strony')
            html_uri = html.p(msg[1])
            html_symfony_action = html.h3(html.span('Modul: ') + html.b(msg[2]) + html.span(' Akcja: ') + html.b(msg[3]))
            html_delete_link = html.a('Usun podobne bledy', href='/trac/bugs?delete_bug_id=' + arguments[0])
            html_error = html.div(html_msg_h3 + html_msg + html_uri_h3 + html_uri + html_symfony_action + html_delete_link, class_='ticket_symfony_box')
            return html_error
        else:
            return 'Brak bledu o podanym identyfikatorze: ' + arguments[0]

        return html_url
