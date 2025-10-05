import base64
import io
import os
import random
import subprocess
from pathlib import Path

import requests
from django.conf import settings
from django.core.management.base import BaseCommand
from openai import OpenAI
from PIL import Image

from main.models import Person


def generate_person_image(person: Person, force: bool = False) -> None:
    """
    Generate a headshot image for a person using OpenAI's Image Generation API.

    The function checks if an image already exists for the person (unless force=True),
    generates a new image, downloads it, resizes to 512x512, optimizes, and saves as
    a JPG file.
    """
    image_directory = Path(settings.BASE_DIR) / "static" / "images" / "people"
    image_path = image_directory / f"{person.slug}.jpg"

    if image_path.exists() and not force:
        print(f"  Image already exists for {person.name}, skipping...")
        return

    print(f"  Generating image for {person.name}...")

    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    # Random elements for variety.
    colors = [
        "emerald green",
        "golden yellow",
        "chocolate brown",
        "jet black",
        "bright orange",
        "copper",
        "olive green",
        "tan",
        "ruby red",
        "sapphire blue",
        "pearl white",
        "charcoal gray",
        "burgundy",
        "teal",
        "lime green",
        "bronze",
        "silver",
        "platinum",
        "coral",
        "lavender",
        "turquoise",
        "amber",
        "crimson",
        "indigo",
        "forest green",
    ]

    accessories = [
        "a stylish hat",
        "modern glasses",
        "a colorful scarf",
        "a smart watch",
        "a bow tie",
        "earrings",
        "wireless headphones",
        "a bandana",
        "a baseball cap",
        "sunglasses",
        "a beanie",
        "a tie",
        "a pocket square",
        "a necklace",
        "a backpack",
        "a tablet",
        "a messenger bag",
        "a lanyard",
        "a smart ring",
        "a tote bag",
        "a bracelet",
        "a badge pin",
        "a laptop bag",
        "a fitness tracker",
        "noise-canceling earbuds",
    ]

    backgrounds = [
        "a busy city street",
        "a cozy home office",
        "a modern corporate office",
        "a city bus",
        "a trendy coffee shop",
        "a public library",
        "a sunny park",
        "a coworking space",
        "a conference room",
        "a bookstore",
        "a tech startup office",
        "a university campus",
        "a subway station",
        "a rooftop terrace",
        "a coding bootcamp classroom",
        "a hackathon venue",
        "a maker space",
        "a food truck area",
        "a bike path",
        "an airport lounge",
        "a hotel lobby",
        "a train car",
        "a climbing gym",
        "a game cafe",
        "a beer garden",
    ]

    clothes = [
        "blue jeans and a gray t-shirt",
        "black jeans and a white t-shirt",
        "dark jeans and a blue t-shirt",
        "jeans and a red t-shirt",
        "jeans and a green t-shirt",
        "jeans and a black t-shirt",
        "blue jeans and a navy t-shirt",
        "jeans and a purple t-shirt",
        "dark jeans and a maroon t-shirt",
        "jeans and a yellow t-shirt",
        "black jeans and a dark green t-shirt",
        "blue jeans and an orange t-shirt",
        "jeans and a brown t-shirt",
        "dark jeans and a teal t-shirt",
        "jeans and a plain white shirt",
        "a button-down shirt and slacks",
        "a blazer and dress pants",
        "a suit jacket and trousers",
        "a hoodie and jeans",
        "a flannel shirt and chinos",
        "a polo shirt and khakis",
        "a cardigan and dark jeans",
        "a denim jacket and black pants",
        "a leather jacket and jeans",
        "a sweater and corduroy pants",
        "a bomber jacket and slim pants",
        "a henley shirt and cargo pants",
        "a vest and dress shirt",
        "a turtleneck and slacks",
        "joggers and a sweatshirt",
    ]

    snake_color = random.choice(colors)
    accessory = random.choice(accessories)
    background = random.choice(backgrounds)
    outfit = random.choice(clothes)

    prompt = f"""Please generate a realistic-looking photo of a {person.gender} {snake_color} humanoid Python snake of a member of my Python meetup called "{person.name}". The image should not be unflattering to the person. Do not include the person's name in the image. Dress the Python in {outfit}. The setting is {background}, make it look like something that tech workers find themselves into, in work or in life. Make it slightly unexpected. Give the snake {accessory}."""
    print(prompt)

    response = client.images.generate(
        model="gpt-image-1",
        prompt=prompt,
        size="1024x1024",
        n=1,
    )

    image_data_item = response.data[0]

    print(f"  Processing and saving image to {image_path}...")
    if image_data_item.url:
        print("  Downloading image from URL...")
        image_response = requests.get(image_data_item.url, timeout=30)
        image_response.raise_for_status()
        image = Image.open(io.BytesIO(image_response.content))
    elif image_data_item.b64_json:
        print("  Decoding base64 image data...")
        image_bytes = base64.b64decode(image_data_item.b64_json)
        image = Image.open(io.BytesIO(image_bytes))
    else:
        raise ValueError(
            f"OpenAI API did not return an image URL or base64 data. Response: {response.model_dump()}"
        )

    image = image.convert("RGB")

    image = image.resize((512, 512), Image.Resampling.LANCZOS)

    image.save(image_path, "JPEG", quality=85, optimize=True)

    print(f"  Running jpegoptim on {image_path}...")
    subprocess.run(
        ["jpegoptim", "--strip-all", str(image_path)],
        check=True,
        capture_output=True,
    )

    print(f"  Successfully generated image for {person.name}")


class Command(BaseCommand):
    help = "Generate headshot images for people using OpenAI's DALL-E API."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Regenerate images even if they already exist",
        )
        parser.add_argument(
            "--slug",
            type=str,
            help="Generate image for a specific person by slug",
        )
        parser.add_argument(
            "--limit",
            type=int,
            help="Limit the number of images to generate",
        )

    def handle(self, *args, **options):
        """
        Generate headshot images for all people (or a specific person) who don't have images yet.

        This command iterates through Person objects, checks for missing images in the
        static/images/people/ directory, and generates them using OpenAI's DALL-E API.
        Generated images are resized to 512x512 and saved as optimized JPG files.
        """
        force = options["force"]
        slug = options.get("slug")
        limit = options.get("limit")

        if not os.environ.get("OPENAI_API_KEY"):
            self.stderr.write(
                self.style.ERROR("OPENAI_API_KEY environment variable is not set")
            )
            return

        if slug:
            try:
                person = Person.objects.get(slug=slug)
                people = [person]
            except Person.DoesNotExist:
                self.stderr.write(
                    self.style.ERROR(f"Person with slug '{slug}' does not exist")
                )
                return
        else:
            people = Person.objects.all()

        if isinstance(people, list):
            count = len(people)
        else:
            count = people.count()

        print(f"Processing up to {count} people...")

        generated_count = 0
        for person in people:
            if limit and generated_count >= limit:
                break

            try:
                image_directory = (
                    Path(settings.BASE_DIR) / "static" / "images" / "people"
                )
                image_path = image_directory / f"{person.slug}.jpg"

                if image_path.exists() and not force:
                    print(f"  Image already exists for {person.name}, skipping...")
                    continue

                generate_person_image(person, force=force)
                generated_count += 1
            except Exception as exception:
                self.stderr.write(
                    self.style.ERROR(
                        f"Failed to generate image for {person.name}: {exception}"
                    )
                )
                continue

        print(f"Done! Generated {generated_count} images.")
