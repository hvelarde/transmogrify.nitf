#! /bin/sh

I18NDOMAIN="transmogrify.nitf"

# Synchronise the templates and scripts with the .pot.
# All on one line normally:
bin/i18ndude rebuild-pot --pot src/transmogrify/nitf/locales/${I18NDOMAIN}.pot \
    --create ${I18NDOMAIN} \
   .

# Synchronise the resulting .pot with all .po files
for po in src/transmogrify/nitf/locales/*/LC_MESSAGES/${I18NDOMAIN}.po; do
    bin/i18ndude sync --pot src/transmogrify/nitf/locales/${I18NDOMAIN}.pot $po
done
