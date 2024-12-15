set -e

#
# Create user for application.
#
if [ -n "$APP_USER" ] &&  [ -n "$APP_USER_PASSWORD" ]; then
  echo "Creating user for app...";
  psql -v ON_ERROR_STOP=1 -U $POSTGRES_USER -d $POSTGRES_DB <<-EOSQL
      CREATE USER $APP_USER WITH PASSWORD '$APP_USER_PASSWORD';
      ALTER USER $APP_USER CREATEDB;
      GRANT ALL PRIVILEGES ON DATABASE $POSTGRES_DB TO $APP_USER;
      GRANT CREATE ON SCHEMA public TO $APP_USER;
EOSQL
else
    echo "Variables for app user was not provided. User was not created.";
fi