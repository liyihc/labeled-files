# labeled-files

A little to help me manage files by labels

Support:

- Drag and drop files to manage
  - Move
  - Copy
  - Link
- Filter by mutiple tags
- Nested tags and tree view.
  - If you define two tags `A/BB/CC` and `A/CC`, the tree view maybe like
    - A
      - BB
        - CC
      - CC
- Default workspace
  - by rename json to `config.json` and add you own storage
- Backward compatible
  - All values are storaged in sqlite
  - Auto upgrade sqlite files