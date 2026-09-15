import random

import anthropic
from django.core.management.base import BaseCommand

from main.models import Person

# Deliberately mundane themes. The three fixed examples in the prompt pull every bio
# towards the same handful of gags, and temperature is already at its maximum, so a
# random theme per call is the remaining lever for variety. Mundane themes clash with
# the tech content, which is where the humour comes from.
THEMES = [
    "γραφειοκρατία",
    "φαγητό",
    "ποδόσφαιρο",
    "στρατός",
    "ζωή στο χωριό",
    "πλοία της γραμμής",
    "φόροι",
    "καιρός",
    "γάτες",
    "καραόκε",
    "οδοντίατροι",
    "οδηγοί λεωφορείων",
    "γάμοι",
    "λαχεία",
    "σούπερ μάρκετ",
    "υδραυλικά",
]


def get_bio(name: str, theme: str) -> str:
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

Another example, this speaker's name is "Γιάννης Παπαδόπουλος". The bio should be:

Ο θρύλος λέει ότι ο Γιάννης δε γεννήθηκε, αλλά ήταν αποτέλεσμα ενός ανήθικου και
μυστικού πειράματος της CIA να φτιάξει τον απόλυτο άνθρωπο γράφοντας το DNA του με το
χέρι.

Δυστυχώς, το πείραμα πήγε όσο καλά μπορούσε να πάει ένα πείραμα στο οποίο γράφεις 3 GB
κώδικα με το χέρι, και ο Γιάννης κατέληξε να δημιουργηθεί σαν κάτι που μπορεί να
περιγραφεί μόνο ως "αν το React ήταν άνθρωπος". Αντιδραστικός, υπέρβαρος, και με
αγκύλωση, μόλις ο Γιάννης κατάλαβε τον εαυτό του ορκίστηκε να αλλάξει.

Έτσι, ο Γιάννης ξανάγραψε όλο το DNA του, μεταμορφώνοντας τον εαυτό του στον Γιάννη 2.0,
που αντί για DNA είχε κώδικα Python, και μπορώντας πλέον να μιλάει με τα φίδια, να έχει
σημαντικό ελεύθερο χώρο, και να μη χρειάζεται να ξαναγράφει όλο το DNA του κάθε λίγο και
λιγάκι.

Σήμερα ο Γιάννης προγραμματίζει σε Python, ασχολείται με βιοπληροφορική, και προσπαθεί
να δώσει στον εαυτό του την ικανότητα να πετάει αεριωθούμενος κάθε φορά που τρώει
φασόλια.

Now do one like the example, for a speaker called "{name}". The backstory must revolve
around this theme: "{theme}". Don't add Markdown headings, and add two newlines between
paragraphs.
"""
    message = client.messages.create(
        model="claude-fable-5-1",
        max_tokens=4000,
        # Writing a joke bio does not need reasoning, but this model rejects
        # thinking.type "disabled", so low effort with adaptive thinking is the closest
        # we can get to switching it off.
        thinking={"type": "adaptive"},
        output_config={"effort": "low"},
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
    # This model thinks by default and refuses to have thinking switched off, so the
    # first content block is a thinking block, not the bio. Select the text block.
    return [block for block in message.content if block.type == "text"][0].text


class Command(BaseCommand):
    help = "Fill out empty bios."

    def handle(self, *args, **options):
        """
        Fill out empty bios.
        """
        print("Filling out empty bios...")
        for person in Person.objects.filter(bio=""):
            theme = random.choice(THEMES)
            print(f"Filling out bio for {person.name} (theme: {theme})...")
            bio = get_bio(person.name, theme)
            print(bio)
            person.bio = bio
            person.save()
