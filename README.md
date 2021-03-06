Backend end for Friend Them App 2.0

## Setup
0. `git clone`
1. `pyenv virtualenv friendthem && pyenv activate friendthem`
2. `pip install requirements.txt`
3. `cp contrib/postactivate{.sample,}` and configure this file with the correct keys
3. `source contrib/postactivate`
4. `createdb friendthem`
5. `python project/manage.py migrate`

### PostGIS Setup

At Ubuntu 14.04

```bash
$ sudo apt-get install postgresql-9.5-postgis-2.2 pgadmin3 postgresql-contrib-9.5
$ createdb simulingua
$ psql simulingua -c "CREATE EXTENSION postgis;"
```

At Mac OS X (with Homebrew)

```bash
$ brew install postgis
$ brew install gdal
$ brew install libgeoip
```

### Deploy

```
git flow release start <release number>
git flow release finish <release number>
git push origin develop && git checkout master && git push origin master && git push origin --tags

# Make release notes in github.

git push dev v<>version_number>^{}:master
# QA in dev.
git push staging v<>version_number>^{}:master
# QA staging
# Push to production
git push production v<version_number>^{}:master
