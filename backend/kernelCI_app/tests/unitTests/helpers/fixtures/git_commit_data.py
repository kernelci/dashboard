MERGE_COMMIT_HASH = "0123456789abcdef0123456789abcdef01234567"
FIRST_PARENT = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
SECOND_PARENT = "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"

# gpgsig uses space-prefixed continuation lines, including a "blank" signature line.
MERGE_COMMIT_OBJECT = (
    "tree 4b825dc642cb6eb9a060e54bf8d69288fbee4904\n"
    "parent aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\n"
    "parent bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb\n"
    "author Alice Author <alice@example.com> 1000000000 +0000\n"
    "committer Bob Committer <bob@example.com> 1000000060 -0500\n"
    "gpgsig -----BEGIN PGP SIGNATURE-----\n"
    " \n"
    " iQIzBAABCAAdFiEE\n"
    " -----END PGP SIGNATURE-----\n"
    "\n"
    "Add feature foo\n"
    "\n"
    "Longer body that is not the subject.\n"
)
