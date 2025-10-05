# PyThess Django Project Guide

## Commands
- **Run server**: `python manage.py runserver`
- **Tests**: `python manage.py test`
- **Run specific test**: `python manage.py test main.tests.SomeTestClass.test_method`
- **Create migrations**: `python manage.py makemigrations`
- **Apply migrations**: `python manage.py migrate`
- **Shell**: `python manage.py shell`

## Code Style
- **PEP 8** guidelines for Python code
- **Imports**: Group by stdlib, Django, third-party, local (separate with blank line)
- **Classes**: PascalCase (e.g., `Event`, `Person`)
- **Functions/Variables**: snake_case (e.g., `get_absolute_url`)
- **Strings**: Double quotes preferred
- **Indentation**: 4 spaces
- **Models**: Include `__str__` method, use Meta class for options
- **URLs**: Use named URL patterns with reverse() for links
- **Error handling**: Use specific exceptions with context messages

## Project Structure
This is a standard Django project for the PyThess community website with event/presentation tracking.

## Tools

- Use the Playwright MCP to look at the frontend when necessary. A server is running at
  localhost:8000 already.
