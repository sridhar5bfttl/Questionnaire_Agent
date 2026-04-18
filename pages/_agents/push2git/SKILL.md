Description: Ensure the recent code is pushed to github repo and it should never push any secrets or .env or secret files.

Check if any file with .env* or secret file contains any text after the keys
example, openai_api_key = sometext. if you find anything after the key then replace it with keyname_here for above files before pushing it to github

after validation the code shuold be pushed to github