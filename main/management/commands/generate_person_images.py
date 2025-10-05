import base64
import io
import os
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

    prompt = f"""Please generate a realistic-looking headshot of a {person.gender} humanoid Python snake of a presenter in my Python meetup called "{person.name}". The image should not be unflattering to the person. Do not include the person's name in the image. Dress the Python up in various plausible Silicon-Valley-tech-worker clothes. Give it a colorful backdrop of everyday locations, e.g. a street, a home, an office, a bus, or whatever other random location you can think of."""

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
