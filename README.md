# FFF-Manager

The **"FFF-Manager"** project is a Django application designed for hosting online football tournaments. The main purpose of the application is to provide functionality for managing users, teams, tournaments, and games.

### Key Features:
1. **Users** — Participants in tournaments with fields for name, nickname, and Telegram integration for notifications. Users can track their win, loss, and draw statistics, and they can participate in multiple tournaments.
2. **Teams** — Information about football teams, such as country, rating, and gameplay attributes (attack, midfield, defense), with compatibility across different FIFA versions.
3. **Tournaments** — Creation of tournaments with specified rules, schedules, and FIFA versions. Tournaments can include multiple participants and scheduled games.
4. **Games** — Data about each game within a tournament: date, participants, result, and chosen teams.

### Highlights:
- Supports multiple FIFA versions compatible with teams and tournaments.
- Admin panel for easy management of users, teams, and tournaments.
- Clear project structure and support for extensibility, with a modular approach to API and different versions.

The project is designed for those who want to organize and manage online FIFA tournaments, providing a flexible and convenient interface for managing games and participants.

## How to Run the Project Locally

To set up and run the **fff-manager** project locally, follow these steps:

1. **Create a volume directory for the database**:
    Create a directory named `db_vol` in the root of the project to store database volumes:
   
   ```bash
   make create-db-vol
   ```

2. **Build the Docker image**:
    Build the Docker image for the project by running:

    ```bash
    make build
    ```

3. **Create your own docker-compose file**
    Use [docker-compose-example.yaml](docker-compose-example.yaml) for that. Just copy and rename it.
    Then set all the necessary environment variables.

4. **Start the Docker containers**:
    Use Docker Compose to start the containers defined in docker-compose.yml:

    ```bash
    make up
    ```

This will set up and run the project along with all necessary services (like the database) in Docker containers.
You can then access the application and begin using fff-manager locally.
