### Create initial galvanalyser database:

```bash
docker-compose run --rm galvanalyser_app python manage.py create_galvanalyser_db
```


### Create a harvester user (can be shared amongst particular machines)

There is normally only a single harvester user account, which is used by the backend 
server to run harvesters, and which is created by the `create_galvanalyser_db` command 
using the information in the `.env` file. However, there is also the possibility to run 
harvesters not part of the main backend server (i.e. on a tester machine), and this 
command will create new harvester users for this purpose.

```bash
docker-compose run --rm galvanalyser_app python manage.py create_harvester
```

Options:
- `--harvester`
- `--password`


### Run backend tests (including harvester code)

The test-suite runs over a set of battery tester files in the directory specified by 
`GALVANALYSER_HARVESTER_TEST_PATH`

```bash
docker-compose run --rm galvanalyser_app python manage.py test
```


### To run the entire stack for development

```bash
sudo docker-compose -f docker-compose.dev.yml up 
```

The main difference from the production `docker-compose.yml` file is that the developer 
can edit all the code in the frontend and backend files, and this will automatically 
compile and restart the dockerised frontend and backend servers appropriately, useful in 
development.
