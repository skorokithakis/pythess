import anthropic
from django.core.management.base import BaseCommand

from main.models import Person


def get_bio(name: str) -> str:
    client = anthropic.Anthropic()
    prompt = f"""
I run the Thessaloniki Python meetup (called PyThess). I run it in a tongue-in-cheek
style, and we get people presenting at the events. I want to add a short, fictional
backstory/bio for each one. It has to be tongue-in-cheek and maybe tearjerk-y, and it
has to relate to Python or technology somehow. It also has to be in Greek.

For example, this speaker's name is "Σταύρος Κοροκυθάκης". The bio should be:

Ο Σταύρος μεγάλωσε στους υπονόμους της Αθήνας, έχοντας αρουραίους για κατοικίδια και
κατσαρίδες για μύγες. Στα 18 του, αποφάσισε να φύγει από τον υπόνομο και να ανέβει στην
επιφάνεια για να βγάλει δίπλωμα οδήγησης υπονομόπλοιου.

Τότε γνώρισε τον μέντορά του, τον Γιάννη, ο οποίος τον μύησε στη γλώσσα Python, η οποία
άρεσε πολύ στο Σταύρο γιατί θα εκπλησσόσασταν αν μαθαίνατε πόσοι πύθωνες πετιούνται κάθε
μέρα στην τουαλέτα, και καταλήγουν στον υπόνομο. Τα υπόλοιπα, όπως λέμε, είναι ιστορία.

Another example, this speaker's name is "Παναγιώτης Παπαεμμανουήλ". The bio should be:

Ο Παναγιώτης γεννήθηκε μια νύχτα που το φεγγάρι δεν έλαμπε, κυρίως γιατί κατάλαβε ότι
πάει να γεννηθεί ο Παναγιώτης. Δεν είναι τυχαίο που από εκεί βγαίνει η λέξη "lunacy",
ψάχτε το.

Ο Παναγιώτης εν τέλει γεννήθηκε, και μεγάλωσε κιόλας, με αρκετή δυσκολία. Οι γονείς του,
που ήταν απλοί, καθημερινοί άνθρωποι, δε μπορούσαν να διαχειριστούν το γεγονός ότι
ο Παναγιώτης μιλούσε ήδη δύο γλώσσες στους οχτώ μήνες, καμία από τις οποίες δεν ήταν
ανθρώπινη. Η ζωή τους έγινε αρκετά ευκολότερη όταν συνειδητοποίησαν ότι ο Παναγιώτης δεν
ήταν ο Άρχοντας του Σκότους, απλά είχε έφεση προς τα δεδομένα, και ότι η αδυναμία του να
πει "μαμά" ήταν γιατί έχτιζε ένα περίπλοκο γλωσσικό μοντέλο στον εγκέφαλό του. Τελικά οι
πρώτες του ελληνικές λέξεις ήταν "πώς σκατά κάνω iterate στο dataframe;", κάτι για το
οποίο οι γονείς του είχαν μικτά συναισθήματα.

Από τότε ο Παναγιώτης συνέχισε να είναι data scientist μέχρι σήμερα.

Now do one like the example, for a speaker called "{name}". Don't add Markdown headings,
and add two newlines between paragraphs.
"""
    message = client.messages.create(
        model="claude-3-7-sonnet-20250219",
        max_tokens=4000,
        temperature=1,
        system="You are a funny biography writer, writing funny (but not offensive) speaker bios.",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt,
                    }
                ],
            }
        ],
    )
    return message.content[0].text


class Command(BaseCommand):
    help = "Fill out empty bios."

    def handle(self, *args, **options):
        """
        Fill out empty bios.
        """
        print("Filling out empty bios...")
        for person in Person.objects.filter(bio=""):
            print(f"Filling out bio for {person.name}...")
            bio = get_bio(person.name)
            print(bio)
            person.bio = bio
            person.save()
