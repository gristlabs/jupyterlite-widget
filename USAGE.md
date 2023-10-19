The experimental JupyterLite Notebook widget lets you run custom Python code in [JupyterLite](https://jupyterlite.readthedocs.io/), a version of [JupyterLab](https://jupyterlab.readthedocs.io/en/stable/index.html) running entirely in the browser. You can use the full [custom widget plugin API](https://support.getgrist.com/code/modules/grist_plugin_api/) and access or modify any data in the document (subject to Access Rules), unlocking nearly unlimited possibilities for advanced users.

In the custom widget configuration, choose “Custom URL” and paste the following URL:

https://gristlabs.github.io/jupyterlite-widget/lab/index.html

You’ll be presented with a blank notebook where you can enter and run Python code, e.g:

![Blank notebook](./images/Screenshot%20from%202023-10-06%2014-38-15.png)

After typing code in a cell, click the play button or press Shift+Enter to run that cell.

Unlike formulas, code isn’t saved automatically. You must press the usual ‘Save’ button above the widget (outside the notebook) to persist the code within your Grist document. On the other hand, changes to settings within the notebook (e.g. keyboard shortcuts) are saved in your browser’s local storage, so they’re not shared with other users of the document.

A special object called `grist` is automatically available to use in Python code. In particular, `grist.raw` provides the usual [plugin API](https://support.getgrist.com/code/modules/grist_plugin_api/). All the methods are asynchronous, so you should use `await` before every call.

### Callbacks

You can decorate functions to make them run automatically when data is changed or the cursor moves in a selected widget. For example, run this code:

```
@grist.on_record
async def show_record(show, record, column_mappings):
    show(record)
```

Then under the Data section in the right panel, click the “SELECT BY” dropdown and choose another widget. If there aren’t any options, add a widget to the page whose source data is the same table as that of the notebook widget. Now when you move the cursor between rows in the other widget, the notebook should automatically update and display the selected row.

Similarly, if you use `@grist.on_records` (note the extra `s` at the end) then the function will automatically run when the source data of the widget changes.

Note that the decorated function must have three arguments. The first argument (called `show` in the example above) should be called to display any kind of outputs instead of calling `print` or `display`. The third argument can be ignored.
