set -e

# extract new phrases
xgettext \
    --from-code=UTF-8 \
    -o humanize.pot \
    -k'_' \
    -k'N_' \
    -k'P_:1c,2' \
    -k'PS_:1c,2' \
    -k'NS_:1,2' \
    -k'_ngettext:1,2' \
    -k'G_:2' \
    -k'NG_:2,3' \
    -l python \
    src/humanize/*.py

# Extract the contextual entries from the same calls without replacing ordinary ones.
xgettext \
    --from-code=UTF-8 \
    --join-existing \
    -o humanize.pot \
    --keyword \
    -k'G_:1c,2' \
    -k'NG_:1c,2,3' \
    -l python \
    src/humanize/*.py

for d in src/humanize/locale/*/; do
    locale="$(basename $d)"
    echo "$locale"
    # add them to locale files
    msgmerge -U src/humanize/locale/$locale/LC_MESSAGES/humanize.po humanize.pot
    # compile to binary .mo
    msgfmt --check -o src/humanize/locale/$locale/LC_MESSAGES/humanize{.mo,.po}
done
