# Forms Examples

Below are examples of various ways to use form with MonsterUI.  `HTMX` can be used to add interactivity and this is an example of the UI components only.


```python
"""FrankenUI Forms Example built with MonsterUI (original design by ShadCN)"""

from fasthtml.common import *
from monsterui.all import *
from fasthtml.svg import *

app, rt = fast_app(hdrs=Theme.blue.headers())

def HelpText(c): return P(c,cls=TextPresets.muted_sm)

def heading():
    return Div(cls="space-y-5")(
            H2("Settings"),
            Subtitle("Manage your account settings and set e-mail preferences."),
            DividerSplit())


sidebar = NavContainer(
    *map(lambda x: Li(A(x)), ("Profile", "Account", "Appearance", "Notifications", "Display")),
    uk_switcher="connect: #component-nav; animation: uk-animation-fade",
    cls=(NavT.secondary,"space-y-4 p-4 w-1/5"))


def FormSectionDiv(*c, cls='space-y-2', **kwargs): return Div(*c, cls=cls, **kwargs)

def FormLayout(title, subtitle, *content, cls='space-y-3 mt-4'): return Container(Div(H3(title), Subtitle(subtitle), DividerLine(), Form(*content, cls=cls)))

def profile_form():
    content = (FormSectionDiv(
            LabelInput("Username", placeholder='sveltecult', id='username'),
            HelpText("This is your public display name. It can be your real name or a pseudonym. You can only change this once every 30 days.")),
        FormSectionDiv(
            LabelSelect(
                      Option("Select a verified email to display", value="", selected=True, disabled=True),
                     *[Option(o, value=o) for o in ('m@example.com', 'm@yahoo.com', 'm@cloud.com')],  
                     label="Email", id="email"),
            HelpText("You can manage verified email addresses in your email settings.")),
        FormSectionDiv(
            LabelTextArea("Bio", id="bio", placeholder="Tell us a little bit about yourself"),
            HelpText("You can @mention other users and organizations to link to them."),
            P("String must contain at least 4 character(s)", cls="text-destructive")),
        FormSectionDiv(
            FormLabel("URLs"),
            HelpText("Add links to your website, blog, or social media profiles."),
            Input(value="https://www.franken-ui.dev"),
            Input(value="https://github.com/sveltecult/franken-ui"),
            Button("Add URL")),
            Button('Update profile', cls=ButtonT.primary))
    
    return FormLayout('Profile', 'This is how others will see you on the site.', *content)

def account_form():
    content = (
        FormSectionDiv(
            LabelInput("Name", placeholder="Your name", id="name"),
            HelpText("This is the name that will be displayed on your profile and in emails.")),
        FormSectionDiv(
            LabelInput("Date of Birth", type="date", placeholder="Pick a date", id="date_of_birth"),
            HelpText("Your date of birth is used to calculate your age.")),
        FormSectionDiv(
            LabelSelect(*Options("Select a language", "English", "French", "German", "Spanish", "Portuguese", selected_idx=1, disabled_idxs={0}),
                          label='Language', id="language"),
            HelpText("This is the language that will be used in the dashboard.")),
        Button('Update profile', cls=ButtonT.primary))
    
    return FormLayout('Account', 'Update your account settings. Set your preferred language and timezone.', *content)

def appearance_form():
    def theme_item(bg_color, content_bg, text_bg):
        common_content = f"space-y-2 rounded-md {content_bg} p-2 shadow-sm"
        item_row = lambda: Div(cls=f"flex items-center space-x-2 {common_content}")(
            Div(cls=f"h-4 w-4 rounded-full {text_bg}"),
            Div(cls=f"h-2 w-[100px] rounded-lg {text_bg}"))
        
        return Div(cls=f"space-y-2 rounded-sm {bg_color} p-2")(
            Div(cls=common_content)(
                Div(cls=f"h-2 w-[80px] rounded-lg {text_bg}"),
                Div(cls=f"h-2 w-[100px] rounded-lg {text_bg}")),
            item_row(),
            item_row())
    
    common_toggle_cls = "block cursor-pointer items-center rounded-md border-2 border-muted p-1 ring-ring"

    content = (
        FormSectionDiv(
            LabelSelect(*Options('Select a font family', 'Inter', 'Geist', 'Open Sans', selected_idx=2, disabled_idxs={0}),
            label='Font Family', id='font_family'), 
            HelpText("Set the font you want to use in the dashboard.")),
        FormSectionDiv(
            FormLabel("Theme"),
            HelpText("Select the theme for the dashboard."),
            Grid(
                A(id="theme-toggle-light", cls=common_toggle_cls)(theme_item("bg-[#ecedef]", "bg-white", "bg-[#ecedef]")),
                A(id="theme-toggle-dark", cls=f"{common_toggle_cls} bg-popover")(theme_item("bg-slate-950", "bg-slate-800", "bg-slate-400")),
                cols_max=2,cls=('max-w-md','gap-8'))),
            Button('Update preferences', cls=ButtonT.primary))
    
    return FormLayout('Appearance', 'Customize the appearance of the app. Automatically switch between day and night themes.', *content)


notification_items = [
    {"title": "Communication emails", "description": "Receive emails about your account activity.", "checked": False, "disabled": False},
    {"title": "Marketing emails", "description": "Receive emails about new products, features, and more.", "checked": False, "disabled": False},
    {"title": "Social emails", "description": "Receive emails for friend requests, follows, and more.", "checked": True, "disabled": False},
    {"title": "Security emails", "description": "Receive emails about your account activity and security.", "checked": True, "disabled": True}]

def notifications_form():
    def RadioLabel(label): return DivLAligned(Radio(name="notification", checked=(label=="Nothing")), FormLabel(label))

    def NotificationCard(item):
        return Card(
            Div(cls="space-y-0.5")(
                FormLabel(Strong(item['title'], cls=TextT.sm),
                HelpText(item['description']))))
    content = Div(
        FormSectionDiv(
            FormLabel("Notify me about"),
            *map(RadioLabel, ["All new messages", "Direct messages and mentions", "Nothing"])),
        Div(
            H4("Email Notifications", cls="mb-4"),
            Grid(*map(NotificationCard, notification_items), cols=1)),
            LabelCheckboxX("Use different settings for my mobile devices", id="notification_mobile"),
            HelpText("You can manage your mobile notifications in the mobile settings page."),
            Button('Update notifications', cls=ButtonT.primary))
    
    return FormLayout('Notifications', 'Configure how you receive notifications.', *content)

def display_form():
    content = (
        Div(cls="space-y-2")(
            Div(cls="mb-4")(
                H5("Sidebar"),
                Subtitle("Select the items you want to display in the sidebar.")),
            *[Div(CheckboxX(id=f"display_{i}", checked=i in [0, 1, 2]),FormLabel(label))
              for i, label in enumerate(["Recents", "Home", "Applications", "Desktop", "Downloads", "Documents"])]),
            Button('Update display', cls=ButtonT.primary))
    return FormLayout('Display', 'Turn items on or off to control what\'s displayed in the app.', *content)

@rt
def index():
    return Title("Forms Example"),Container(
        heading(),
        Div(cls="flex gap-x-12")(
            sidebar,
                Ul(id="component-nav", cls="uk-switcher max-w-2xl")(
                    Li(cls="uk-active")(profile_form(),
                    *map(Li, [account_form(), appearance_form(), notifications_form(), display_form()])))))

serve()
```