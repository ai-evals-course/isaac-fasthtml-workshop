# Cards Examples

Below are examples of various ways to use cards with MonsterUI.  `HTMX` can be used to add interactivity and this is an example of the UI components only.

```python
"""FrankenUI Cards Example built with MonsterUI (original design by ShadCN)"""

from fasthtml.common import *
from fasthtml.components import Uk_input_tag

# This import is needed for SVGs in fasthtml
from fasthtml.svg import *

from monsterui.all import *
import calendar
from datetime import datetime

from svg_data import PaypalSVG_data, AppleSVG_data
app, rt = fast_app(hdrs=Theme.blue.headers())

CreateAccount = Card(
    Grid(Button(DivLAligned(UkIcon('github'),Div('Github'))),Button('Google')),
            DividerSplit("OR CONTINUE WITH", text_cls=TextPresets.muted_sm),
            LabelInput('Email',    id='email',   placeholder='m@example.com'),
            LabelInput('Password', id='password',placeholder='Password', type='Password'),
            header=(H3('Create an Account'),Subtitle('Enter your email below to create your account')),
            footer=Button('Create Account',cls=(ButtonT.primary,'w-full')))

Card1Svg  = Svg(viewBox="0 0 24 24", fill="none", stroke="currentColor", stroke_linecap="round", stroke_linejoin="round", stroke_width="2", cls="h-6 w-6 mr-1")(Rect(width="20", height="14", x="2", y="5", rx="2"),Path(d="M2 10h20"))
PaypalSvg = Svg(role="img", viewBox="0 0 24 24", cls="h-6 w-6 mr-1")(Path(d=PaypalSVG_data, fill="currentColor")),
AppleSvg  = Svg(role="img", viewBox="0 0 24 24", cls="h-6 w-6 mr-1")(Path(d=AppleSVG_data, fill="currentColor"))

PaymentMethod = Card(
    Grid(Button(DivCentered(Card1Svg,  "Card"),   cls='h-20 border-2 border-primary'),
         Button(DivCentered(PaypalSvg, "PayPal"), cls='h-20'),
         Button(DivCentered(AppleSvg,  "Apple"),  cls='h-20')),
    Form(LabelInput('Name',        id='name',        placeholder='John Doe'),
         LabelInput('Card Number', id='card_number', placeholder='m@example.com'),
         Grid(LabelSelect(*Options(*calendar.month_name[1:],selected_idx=0),label='Expires',id='expire_month'),
              LabelSelect(*Options(*range(2024,2030),selected_idx=0),       label='Year',   id='expire_year'),
              LabelInput('CVV', id='cvv',placeholder='CVV', cls='mt-0'))),
        header=(H3('Payment Method'),Subtitle('Add a new payment method to your account.')))

area_opts = ('Team','Billing','Account','Deployment','Support')
severity_opts = ('Severity 1 (Highest)', 'Severity 2', 'Severity 3', 'Severity 4 (Lowest)')
ReportIssue = Card(
    Grid(Div(LabelSelect(*Options(*area_opts),    label='Area',    id='area')),
         Div(LabelSelect(*Options(*severity_opts),label='Severity',id='area'))),
    LabelInput(    label='Subject',     id='subject',    placeholder='I need help with'),
    LabelTextArea( label='Description', id='description',placeholder='Please include all information relevant to your issue'),
    Div(FormLabel('Tags', fr='#tags'),
        Uk_input_tag(name="Tags",state="danger", value="Spam,Invalid", uk_cloak=True, id='tags')),
    header=(H3('Report Issue'),Subtitle('What area are you having problems with?')),
    footer = DivFullySpaced(Button('Cancel'), Button(cls=ButtonT.primary)('Submit')))

monster_desc ="Python-first beautifully designed components because you deserve to focus on features that matter and your app deserves to be beautiful from day one."
MonsterUI = Card(H4("Monster UI"),
              Subtitle(monster_desc),
              DivLAligned(
                    Div("Python"),
                    DivLAligned(UkIcon('star'),Div("20k"), cls='space-x-1'),
                    Div(datetime.now().strftime("%B %d, %Y")),
                    cls=('space-x-4',TextPresets.muted_sm)))

def CookieTableRow(heading, description, active=False):
    return Tr(Td(H5(heading)),
              Td(P(description, cls=TextPresets.muted_sm)),
              Td(Switch(checked=active)))

CookieSettings = Card(
    Table(Tbody(
        CookieTableRow('Strictly Necessary', 'These cookies are essential in order to use the website and use its features.', True),
        CookieTableRow('Functional Cookies', 'These cookies allow the website to provide personalized functionality.'),
        CookieTableRow('Performance Cookies', 'These cookies help to improve the performance of the website.'))),
    header=(H4('Cookie Settings'),Subtitle('Manage your cookie settings here.')),
    footer=Button('Save Preferences', cls=(ButtonT.primary, 'w-full')))

team_members = [("Sofia Davis", "m@example.com", "Owner"),("Jackson Lee", "p@example.com", "Member"),]
def TeamMemberRow(name, email, role):
    return DivFullySpaced(
        DivLAligned(
            DiceBearAvatar(name, 10,10),
            Div(P(name, cls=(TextT.sm, TextT.medium)),
                P(email, cls=TextPresets.muted_sm))),
        Button(role, UkIcon('chevron-down', cls='ml-4')),
        DropDownNavContainer(map(NavCloseLi, [
            A(Div('Viewer',    NavSubtitle('Can view and comment.'))),
            A(Div('Developer', NavSubtitle('Can view, comment and edit.'))),
            A(Div('Billing',   NavSubtitle('Can view, comment and manage billing.'))),
            A(Div('Owner',     NavSubtitle('Admin-level access to all resources.')))])))

TeamMembers = Card(*[TeamMemberRow(*member) for member in team_members],
        header = (H4('Team Members'),Subtitle('Invite your team members to collaborate.')))

access_roles = ("Read and write access", "Read-only access")
team_members = [("Olivia Martin", "m@example.com", "Read and write access"),
                ("Isabella Nguyen", "b@example.com", "Read-only access"),
                ("Sofia Davis", "p@example.com", "Read-only access")]

def TeamMemberRow(name, email, role):
    return DivFullySpaced(
        DivLAligned(DiceBearAvatar(name, 10,10),
                    Div(P(name, cls=(TextT.sm, TextT.medium)),
                        P(email, cls=TextPresets.muted_sm))),
        Select(*Options(*access_roles, selected_idx=access_roles.index(role))))

ShareDocument = Card(
    DivLAligned(Input(value='http://example.com/link/to/document'),Button('Copy link', cls='whitespace-nowrap')),
    Divider(),
    H4('People with access', cls=TextPresets.bold_sm),
    *[TeamMemberRow(*member) for member in team_members],
    header = (H4('Share this document'),Subtitle('Anyone with the link can view this document.')))

DateCard = Card(Button('Jan 20, 2024 - Feb 09, 2024'))

section_content =(('bell','Everything',"Email digest, mentions & all activity."), 
                  ('user',"Available","Only mentions and comments"),
                  ('ban', "Ignoring","Turn of all notifications"))

def NotificationRow(icon, name, desc):
    return Li(cls='-mx-1')(A(DivLAligned(UkIcon(icon),Div(P(name),P(desc, cls=TextPresets.muted_sm)))))

Notifications = Card(
    NavContainer(
        *[NotificationRow(*row) for row in section_content],
        cls=NavT.secondary),
    header = (H4('Notification'),Subtitle('Choose what you want to be notified about.')),
    body_cls='pt-0')

TeamCard = Card(
    DivLAligned(
        DiceBearAvatar("Isaac Flath", h=24, w=24),
        Div(H3("Isaac Flath"), P("Library Creator"))),
    footer=DivFullySpaced(
        DivHStacked(UkIcon("map-pin", height=16), P("Alexandria, VA")),
        DivHStacked(*(UkIconLink(icon, height=16) for icon in ("mail", "linkedin", "github")))),
    cls=CardT.hover)

@rt
def index():
    return Title("Cards Example"),Container(Grid(
            *map(Div,(
                      Div(PaymentMethod,CreateAccount, TeamCard, cls='space-y-4'),
                      Div(TeamMembers, ShareDocument,DateCard,Notifications, cls='space-y-4'),
                      Div(ReportIssue,MonsterUI,CookieSettings, cls='space-y-4'))),
         cols_md=1, cols_lg=2, cols_xl=3))

serve()
```