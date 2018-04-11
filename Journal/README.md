# Journal

In addition to the scripts here, I also have [this Workflow](https://workflow.is/workflows/f7cd90eac8864398a51ac4a9ac4286ed) and the following Drafts 4 action:

## Add Journal Entry (Drafts action)

URL: `working-copy://x-callback-url/write?text=[[body]]&key={{123456}}&repo={{journal}}&path=[[title]]&x-success={{pythonista://Journal/Generate%20HTML.py?action=run}}`

*Note:* the `key` parameter needs to be set to the Working Copy x-callback-url key.

## Additional Files

The `Generate HTML.py` script looks for the files `working_copy_key.txt` and `working_copy_webdav_password.txt` in the working directory. 