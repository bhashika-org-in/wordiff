# wordiff

Word-level diff rendered as HTML and opened in your browser. Single Python file, standard library only.

Built with proofreading and Indic text in mind: combining marks and ZWJ/ZWNJ stay glued to their word, so `हिंदी` diffs as one token while the danda (`।`) stays a separate token. Invisible joiners render as visible `⟨zwj⟩` / `⟨zwnj⟩` markers.

## Install

Copy `wordiff` anywhere on your `PATH` and make it executable:

```sh
cp wordiff ~/.local/bin/
chmod +x ~/.local/bin/wordiff
```

Requires Python 3, no dependencies.

## Use

```sh
wordiff OLD NEW          # two files
wordiff OLD_DIR NEW_DIR  # two directories, one page with a file summary
printf 'new text\n' | wordiff OLD -   # stdin as the new file
printf 'old text\n' | wordiff - NEW   # stdin as the old file
```

By default the report opens in a browser. The HTML path is always printed, so `--no-browser --output report.html` gives you just the file.

| Flag | Meaning |
|---|---|
| `--context N` | Unchanged lines around each hunk (default 3) |
| `--mode unified` | Changed lines as `-`/`+` pairs (default) |
| `--mode inline` | Each change merged into one `~` line |
| `--normalize nfc\|nfd\|nfkc\|nfkd` | Unicode-normalize both inputs before diffing |
| `--ignore-punct` | Hide changes that touch punctuation only |
| `--output FILE` | Write HTML here instead of a temp file |
| `--no-browser` | Don't open a browser |
| `--browser CMD` | Custom browser command, e.g. `--browser 'chromium --ozone-platform=x11'` |
| `--title T`, `--label-old`, `--label-new` | Override the page/file headings |

Limits: files are compared through their first 2000 lines, binary files are reported as "Binary files differ", and temp reports accumulate in your temp dir unless `--output` is given.

## Use with git

Whole diff as one page, no setup:

```sh
git difftool --dir-diff -x wordiff
```

Persistent config (per-file view, one tab per file):

```sh
git config --global difftool.wordiff.cmd 'wordiff "$LOCAL" "$REMOTE"'
git difftool -t wordiff
```

Adding switches: `-x` takes a bare command, so switches go through `difftool.<tool>.cmd`, which runs via a shell. Put flags before the quoted `$LOCAL`/`$REMOTE`:

```sh
git config --global difftool.wordiff.cmd \
  'wordiff --mode inline --context 5 --ignore-punct "$LOCAL" "$REMOTE"'
```

One-shot variant without touching your config:

```sh
git -c 'difftool.wordiff.cmd=wordiff --mode inline "$LOCAL" "$REMOTE"' difftool --dir-diff -t wordiff
```

As an external diff driver (per-file view during plain `git diff`; the terminal shows each generated HTML path). Flags go in the env var — wordiff picks them out from around git's 7 positional arguments:

```sh
GIT_EXTERNAL_DIFF='wordiff --mode inline --ignore-punct --no-browser' git diff
```

## Use with jj

Register it as a diff tool (read-only — don't use it for `jj resolve`, since it never writes merge output):

```sh
jj config set --user merge-tools.wordiff.program wordiff
jj diff --tool wordiff
```

Adding switches: set `diff-args` (TOML array, `$left`/`$right` are the snapshots jj passes in). Any wordiff flag works:

```sh
jj config set --user merge-tools.wordiff.diff-args '["--mode", "inline", "--context", "5", "--ignore-punct", "$left", "$right"]'
```

One-shot variant without touching your config:

```sh
jj diff --tool wordiff --config 'merge-tools.wordiff.diff-args=["--mode", "inline", "$left", "$right"]'
```

`jj diff --tool wordiff` passes snapshot directories, so you get the whole change as one page.

## Tests

```sh
python3 -m pytest tests/ -q
```

## License

Apache-2.0 — see [LICENSE](LICENSE).
