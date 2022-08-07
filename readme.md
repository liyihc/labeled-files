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

## Config

This program will automatically create a file `config.json` within the binary folder. 
You can edit it to 
- change default workspace name
- add another workspace
- in results, hide tag which used in searching
- support regex 'r|'
  - I will enrich this feature
  - but now, the matched part will be shown when searching
- path mapping
  
  A sync folder may have different path in different PC, This will change path prefix.
- pc name override
  
  This program 