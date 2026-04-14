### User Stories and Acceptance Tests

## User Story – Fetch a Random Joke
* As a user, I want to fetch a random joke so I can get a quick laugh.

# Acceptance Test
- Given the user clicks “Get Joke”
- When the `/joke` endpoint responds
- Then the joke setup and punchline appear on the page


## User Story – Select a Joke Category
* As a user, I want to choose a joke category so I can find a joke I find funny.


# Acceptance Test
- Given the user selects a category
- When they request a joke
- Then the returned joke matches the selected category
- 

## User Story – Store Joke History
* As a developer, I want to store each joke request so that I can maintain a history of user interactions.

# Acceptance Test
- Given a joke is fetched
- When Flask processes the response
- Then a new row is inserted into `joke_history`
