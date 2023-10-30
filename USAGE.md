The experimental JupyterLite Notebook widget lets you run custom Python code in [JupyterLite](https://jupyterlite.readthedocs.io/), a version of [JupyterLab](https://jupyterlab.readthedocs.io/en/stable/index.html) running entirely in the browser. You can use the full [custom widget plugin API](https://support.getgrist.com/code/modules/grist_plugin_api/) and access or modify any data in the document (subject to Access Rules), unlocking nearly unlimited possibilities for advanced users.

In the custom widget configuration, choose “Custom URL” and paste the following URL:

https://gristlabs.github.io/grist-widget/jupyterlite/

You’ll be presented with a notebook where you can enter and run Python code, e.g:

![Example notebook](./images/Screenshot%20from%202023-10-27%2018-06-30.png)

After typing code in a cell, click the play button or press Shift+Enter to run that cell.

Unlike formulas, code isn’t saved automatically. You must press the usual ‘Save’ button above the widget (outside the notebook) to persist the code within your Grist document. On the other hand, changes to settings within the notebook (e.g. keyboard shortcuts) are saved in your browser’s local storage, so they’re not shared with other users of the document.

A special object called `grist` is automatically available to use in Python code, which mirrors many common methods of the usual [JS plugin API](https://support.getgrist.com/code/modules/grist_plugin_api/). Note that many of these methods are asynchronous, so you should use `await` before calling them.

- `async fetch_selected_table()`: returns the data of the table backing the notebook widget.
- `async fetch_selected_record(row_id=None)`: returns a record of the table backing the notebook widget. If `row_id` is specified, returns the record at that row. Otherwise, returns the record at the current cursor position in a widget linked to the notebook widget.
- `async fetch_table(table_id)`: returns the data of the specified table. Note that this differs from `fetch_selected_table` (even for the same table) in several ways:
  - The widget must have full document access.
  - All columns are included, whereas `fetch_selected_table` excludes columns that are hidden in the widget configuration.
  - All rows are included, whereas `fetch_selected_table` takes widget filters and 'SELECT BY' into account.
  - The data is not sorted according to the widget's configuration.
  - The data is fetched from the server, so the method may be slower.
  - The values for reference columns are row IDs of the referenced table, whereas `fetch_selected_table` returns the values displayed based on the 'SHOW COLUMN' configuration.
- `on_record(callback)`: registers a callback function to run when the cursor moves in a widget linked to the notebook widget, i.e. the widget chosen from the "SELECT BY" dropdown in the Data section of the widget configuration. The callback function will be passed the record at the current cursor position. You can also use this as a decorator, i.e. `@grist.on_record`.
- `on_records(callback)`: similar to `on_record`, but runs when the source data of the widget changes. The callback function will be passed the same data as returned by `fetch_selected_table`.
- `get_table(table_id)`: returns a `TableOperations` class similar to the interface in the usual [JS plugin API](https://support.getgrist.com/code/interfaces/TableOperations.TableOperations/) for performing CRUD-style operations on a table. See the plugin API documentation for details on the parameters. The class has the following methods:
  - `async create(records, parse_strings=True)`
  - `async update(records, parse_strings=True)`
  - `async upsert(records, parse_strings=True, add=True, update=True, on_many="first", allow_empty_require=False)`
  - `async destroy(row_ids)`

You can also use `grist.raw` for direct access to the plugin API, e.g. `await grist.raw.docApi.fetchTable(table_id)`. This may return raw cell values which you can decode with `grist.decode_cell_value(value)`.

You can use many (but not all) third-party libraries in your notebook such as `pandas`. Many will be installed automatically when they're imported. Others will require running `%pip install <package name>` in a cell, e.g. `%pip install pandas`. Note that it's `%pip` and not `!pip` as in a regular Jupyter notebook.
