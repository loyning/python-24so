# API client for 24SevenOffice
There are three services ready
- PersonService
- CompanyService
- ProjectService
For more information: http://developer.24sevenoffice.com/

## API calls
- Searching returns a list with dict or empty list
- Fetching detailed information, ex. find_by_id, returns a dict or None

## Usage
```python
from tfsoffice import Client
from getpass import getpass

username = raw_input('Enter username: ')
password = getpass()
apikey = getpass('Enter your API key: ')

# authenticate
api = Client(username, password, apikey)

# search for person by name
people = api.persons.find_by_name('rune')

if len(people):
    # get detailed info about a person
    person = api.persons.find_by_id(people[0]['Id'])

# list all projects assigned to you
projects = api.projects.find_mine()

# search for a company
customers = api.companies.find_by_name('dataselskapet')

# get detailed information about a company
dataselskapet = api.companies.find_by_id(102)

# list all projects assigned to a company
projects = api.projects.find_by_customerid(102)
```
