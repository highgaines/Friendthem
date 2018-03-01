e2e:
	@echo "Dropping friendthem..."; \
	dropdb friendthem --if-exists
	@echo "Creating friendthem..."; \
	createdb friendthem
	pg_restore --verbose --clean --no-acl --no-owner -h localhost -U root -d friendthem e2e-seed.dump &
	DATABASE_URL="postgres://postgres:postgres@localhost:5432/friendthem" python project/manage.py runserver

e2e-seed:
	pg_dump -Fc friendthem > e2e-seed.dump

coverage:
	cd project && pytest --cov=src && cd -

stagingdump:
	heroku pg:backups capture --app staging-friendthem-api
	curl -o staging.dump `heroku pg:backups public-url --app staging-friendthem-api`

loadstagingdump:
	dropdb friendthemstaging --if-exists
	createdb friendthemstaging
	pg_restore --verbose --clean --no-acl --no-owner -h localhost -U root -d friendthemstaging staging.dump
