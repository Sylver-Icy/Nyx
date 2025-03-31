import re
import database

def autocomplete(query):
    pattern=re.compile(f".*{query}.*")
    return [key for key in database.items if pattern.match(key)]
print(autocomplete("it"))